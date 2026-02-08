"""
Hybrid GPU+NPU inference engine for parallel model execution.
Leverages both NVIDIA RTX 5070 (12GB) and Intel AI Boost NPU (17.9GB shared).
"""

import torch 
import numpy as np 
from typing import Any ,Dict ,List ,Optional ,Tuple 
from concurrent .futures import ThreadPoolExecutor ,as_completed 
import logging 

from utils .gpu_utils import get_device_manager ,is_hybrid_available 

logger =logging .getLogger (__name__ )


class HybridInferenceEngine :
    """
    Executes models in parallel on GPU and NPU for faster inference.
    Automatically distributes workload based on device availability.
    """

    def __init__ (self ,max_workers :int =2 ):
        self .device_manager =get_device_manager ()
        self .max_workers =max_workers if is_hybrid_available ()else 1 
        self .gpu_device ,self .npu_device =self .device_manager .get_all_devices ()
        logger .info (f"HybridInferenceEngine initialized. Workers: {self .max_workers }")

    def infer_ensemble (self ,
    models :List [Any ],
    inputs :torch .Tensor ,
    weights :Optional [List [float ]]=None )->torch .Tensor :
        """
        Run multiple models in parallel on GPU and NPU, then ensemble results.
        
        Args:
            models: List of PyTorch models
            inputs: Input tensor
            weights: Optional weights for ensembling (default: equal)
        
        Returns:
            Ensembled predictions
        """
        if not models :
            raise ValueError ("No models provided")

        if weights is None :
            weights =[1.0 /len (models )]*len (models )


        if len (models )==1 :
            with torch .no_grad ():
                return models [0 ](inputs .to (self .device_manager .get_device ()))


        if self .max_workers >1 :
            return self ._parallel_infer_ensemble (models ,inputs ,weights )
        else :
            return self ._sequential_infer_ensemble (models ,inputs ,weights )

    def _parallel_infer_ensemble (self ,
    models :List [Any ],
    inputs :torch .Tensor ,
    weights :List [float ])->torch .Tensor :
        """Execute models in parallel on GPU and NPU"""
        results =[]
        devices =[self .gpu_device ,self .npu_device ]

        with ThreadPoolExecutor (max_workers =self .max_workers )as executor :
            futures ={}

            for idx ,model in enumerate (models ):
                device =devices [idx %len (devices )]
                future =executor .submit (self ._infer_on_device ,
                model ,inputs ,device ,weights [idx ])
                futures [future ]=idx 


            results =[None ]*len (models )
            for future in as_completed (futures ):
                idx =futures [future ]
                results [idx ]=future .result ()


        stacked =torch .stack (results )
        ensembled =torch .mean (stacked ,dim =0 )
        return ensembled 

    def _sequential_infer_ensemble (self ,
    models :List [Any ],
    inputs :torch .Tensor ,
    weights :List [float ])->torch .Tensor :
        """Execute models sequentially (single device)"""
        results =[]
        device =self .device_manager .get_device ()
        inputs =inputs .to (device )

        with torch .no_grad ():
            for model ,weight in zip (models ,weights ):
                model =model .to (device )
                output =model (inputs )
                results .append (output *weight )

        return torch .sum (torch .stack (results ),dim =0 )

    def _infer_on_device (self ,
    model :Any ,
    inputs :torch .Tensor ,
    device :torch .device ,
    weight :float =1.0 )->torch .Tensor :
        """Run inference on specific device"""
        try :
            model =model .to (device )
            inputs =inputs .to (device )

            with torch .no_grad ():
                output =model (inputs )

            return output *weight 
        except Exception as e :
            logger .error (f"Inference failed on {device }: {e }")
            raise 

    def batch_infer_distributed (self ,
    model :Any ,
    batch_data :List [Dict [str ,Any ]],
    batch_size :int =4 )->List [torch .Tensor ]:
        """
        Process large batch by splitting between GPU and NPU.
        GPU gets larger batches, NPU gets smaller ones.
        """
        if not is_hybrid_available ():
            return self ._batch_infer_single (model ,batch_data ,batch_size )

        gpu_batch_size =int (batch_size *0.7 )
        npu_batch_size =batch_size -gpu_batch_size 

        results =[]

        with ThreadPoolExecutor (max_workers =2 )as executor :

            gpu_batches =[batch_data [i :i +gpu_batch_size ]
            for i in range (0 ,len (batch_data ),gpu_batch_size )]
            gpu_future =executor .submit (self ._batch_infer_single ,
            model ,gpu_batches [0 ]if gpu_batches else [],
            gpu_batch_size )


            npu_batches =batch_data [len (gpu_batches )*gpu_batch_size :]
            npu_future =executor .submit (self ._batch_infer_single ,
            model ,npu_batches ,
            npu_batch_size )

            results .extend (gpu_future .result ())
            results .extend (npu_future .result ())

        return results 

    def _batch_infer_single (self ,
    model :Any ,
    batch_data :List [Dict ],
    batch_size :int )->List [torch .Tensor ]:
        """Inference on single device for batch data"""
        results =[]
        device =self .device_manager .get_device ()
        model =model .to (device )

        with torch .no_grad ():
            for i in range (0 ,len (batch_data ),batch_size ):
                batch =batch_data [i :i +batch_size ]
                if not batch :
                    continue 


                batch_tensor =torch .stack ([
                torch .tensor (item .get ('features',[]),dtype =torch .float32 )
                for item in batch 
                ]).to (device )

                output =model (batch_tensor )
                results .append (output )

        return results 

    def optimize_for_throughput (self ,batch_size :int )->int :
        """
        Recommend optimal batch size based on available memory.
        GPU: 12GB, NPU: 17.9GB shared
        """
        if is_hybrid_available ():

            return min (batch_size *2 ,128 )
        elif self .gpu_device :

            return batch_size 
        else :

            return max (batch_size //2 ,1 )

    def get_device_memory_info (self )->Dict [str ,float ]:
        """Get memory info for both devices"""
        info ={}

        if self .gpu_device :
            try :
                allocated =torch .cuda .memory_allocated ()/1e9 
                reserved =torch .cuda .memory_reserved ()/1e9 
                total =torch .cuda .get_device_properties (0 ).total_memory /1e9 
                info ['gpu_allocated_gb']=allocated 
                info ['gpu_reserved_gb']=reserved 
                info ['gpu_total_gb']=total 
            except :
                pass 

        if self .npu_device :
            info ['npu_shared_gb']=17.9 

        if is_hybrid_available ():
            total =info .get ('gpu_total_gb',0 )+info .get ('npu_shared_gb',0 )
            info ['total_compute_memory_gb']=total 
            info ['hybrid_mode']=True 

        return info 



_hybrid_engine :Optional [HybridInferenceEngine ]=None 


def get_hybrid_engine ()->HybridInferenceEngine :
    """Get or create global hybrid inference engine"""
    global _hybrid_engine 
    if _hybrid_engine is None :
        _hybrid_engine =HybridInferenceEngine ()
    return _hybrid_engine 
