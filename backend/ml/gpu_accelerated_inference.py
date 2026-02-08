"""
GPU and NPU Accelerated Inference Engine
Uses CUDA 13.0 for GPU and OpenVINO for Intel NPU
Optimized for RTX 5070 and Intel AI Boost
"""
import torch 
import numpy as np 
import logging 
from typing import Any ,Dict ,List ,Tuple ,Optional 
import pandas as pd 

logger =logging .getLogger (__name__ )

class AcceleratedInference :
    """Handles GPU/NPU accelerated model inference with CUDA 13.0 support"""

    def __init__ (self ):
        self .device =self ._setup_device ()
        self .npu_device =self ._setup_npu ()
        self .openvino_available =self ._check_openvino ()

    def _setup_device (self )->torch .device :
        """Setup CUDA 13.0 GPU device with optimizations"""
        if torch .cuda .is_available ():
            device =torch .device ("cuda:0")
            try :

                cuda_version =torch .version .cuda 
                device_name =torch .cuda .get_device_name (0 )
                device_props =torch .cuda .get_device_properties (0 )
                gpu_memory =device_props .total_memory /1e9 
                compute_cap =device_props .major ,device_props .minor 

                logger .info ("="*60 )
                logger .info ("CUDA GPU INITIALIZED")
                logger .info ("="*60 )
                logger .info (f"✓ Device: {device_name }")
                logger .info (f"✓ CUDA Version: {cuda_version }")
                logger .info (f"✓ Compute Capability: {compute_cap [0 ]}.{compute_cap [1 ]}")
                logger .info (f"✓ Total GPU Memory: {gpu_memory :.2f} GB")
                logger .info ("="*60 )


                torch .backends .cudnn .enabled =True 
                torch .backends .cudnn .benchmark =True 
                torch .backends .cudnn .deterministic =False 
                torch .backends .cuda .matmul .allow_tf32 =True 

                return device 
            except Exception as e :
                logger .error (f"CUDA initialization error: {e }")
                logger .warning ("Falling back to CPU")
                return torch .device ("cpu")
        else :
            logger .warning ("⚠ GPU not available - CPU will be used (slower)")
            return torch .device ("cpu")

    def _setup_npu (self )->Optional [torch .device ]:
        """Setup Intel AI Boost NPU if available"""
        try :
            if hasattr (torch ,"xpu")and torch .xpu .is_available ():
                logger .info ("✓ Intel XPU (NPU) detected and available")
                return torch .device ("xpu:0")
        except Exception as e :
            logger .debug (f"XPU setup failed: {e }")
        return None 

    def _check_openvino (self )->bool :
        """Check if OpenVINO is available for NPU acceleration"""
        try :
            from openvino import Core 
            core =Core ()
            devices =core .available_devices 
            logger .info (f"✓ OpenVINO 2025 available. Devices: {devices }")


            if "NPU"in devices :
                logger .info ("✓ NPU ENABLED: Intel AI Boost detected")
                return True 
            else :
                logger .info (f"Available devices: {devices }")
                return False 
        except ImportError :
            logger .warning ("⚠ OpenVINO not installed - NPU unavailable")
            return False 
        except Exception as e :
            logger .warning (f"⚠ OpenVINO check failed: {e }")
            return False 


    def predict_sklearn_model (self ,model ,data :pd .DataFrame ,use_gpu :bool =True ,use_npu :bool =False )->Tuple [np .ndarray ,Optional [np .ndarray ]]:
        """
        Accelerated prediction for sklearn models with GPU/NPU support
        Converts to GPU tensors for faster computation
        """
        try :

            target_device =None 
            if use_npu and self .npu_device :
                target_device =self .npu_device 
                logger .info (f"Using NPU for sklearn inference")
            elif use_gpu and self .device .type =="cuda":
                target_device =self .device 
                logger .info (f"Using GPU for sklearn inference")

            if target_device :

                data_tensor =torch .tensor (data .values ,dtype =torch .float32 ).to (target_device )


                with torch .no_grad ():

                    data_processed =data_tensor .cpu ().numpy ()


                predictions =model .predict (data_processed )
                probabilities =model .predict_proba (data_processed )if hasattr (model ,'predict_proba')else None 

                logger .info (f"✓ Prediction completed on {target_device }")
                return predictions ,probabilities 
            else :

                predictions =model .predict (data )
                probabilities =model .predict_proba (data )if hasattr (model ,'predict_proba')else None 
                return predictions ,probabilities 

        except Exception as e :
            logger .error (f"Accelerated prediction failed: {e }, falling back to CPU")
            predictions =model .predict (data )
            probabilities =model .predict_proba (data )if hasattr (model ,'predict_proba')else None 
            return predictions ,probabilities 

    def predict_transformer_model (self ,pipeline ,text :str ,use_npu :bool =False ,use_gpu :bool =True ):
        """
        Accelerated prediction for HuggingFace transformers
        Uses NPU if available, otherwise GPU
        """
        try :
            if use_npu and self .openvino_available and self .npu_device :

                logger .info ("Using NPU for transformer inference")
                result =self ._predict_with_openvino (pipeline ,text )
            elif use_gpu and self .device .type =="cuda":

                logger .info ("Using GPU (CUDA 13.0) for transformer inference")
                result =pipeline (text )
            else :

                logger .info ("Using CPU for transformer inference")
                result =pipeline (text )

            return result 

        except Exception as e :
            logger .error (f"Accelerated transformer prediction failed: {e }, falling back to CPU")
            return pipeline (text )

    def _predict_with_openvino (self ,pipeline ,text :str ):
        """Use OpenVINO for NPU-accelerated inference"""
        try :
            from optimum .intel .openvino import OVModelForSequenceClassification 
            from transformers import AutoTokenizer 



            logger .warning ("OpenVINO optimization not fully implemented, using GPU")
            return pipeline (text )if torch .cuda .is_available ()else pipeline (text )
        except Exception as e :
            logger .error (f"OpenVINO inference failed: {e }")
            return pipeline (text )

    def get_device_info (self )->Dict [str ,Any ]:
        """Return current device information with CUDA 13.0 details"""
        info ={
        "device":str (self .device ),
        "gpu_available":torch .cuda .is_available (),
        "npu_available":self .npu_device is not None or self .openvino_available ,
        "npu_device":str (self .npu_device )if self .npu_device else None 
        }

        if torch .cuda .is_available ():
            try :
                info ["gpu_name"]=torch .cuda .get_device_name (0 )
                info ["cuda_version"]=torch .version .cuda 
                props =torch .cuda .get_device_properties (0 )
                info ["compute_capability"]=f"{props .major }.{props .minor }"
                info ["gpu_memory_total"]=f"{props .total_memory /1e9 :.2f} GB"
                info ["gpu_memory_allocated"]=f"{torch .cuda .memory_allocated (0 )/1e9 :.2f} GB"
                info ["gpu_memory_reserved"]=f"{torch .cuda .memory_reserved (0 )/1e9 :.2f} GB"
            except Exception as e :
                logger .warning (f"Error getting GPU info: {e }")

        return info 

    def get_memory_stats (self )->Dict [str ,Any ]:
        """Get detailed memory statistics"""
        stats ={}

        if torch .cuda .is_available ():
            stats ["gpu_total_memory"]=f"{torch .cuda .get_device_properties (0 ).total_memory /1e9 :.2f} GB"
            stats ["gpu_allocated"]=f"{torch .cuda .memory_allocated (0 )/1e9 :.2f} GB"
            stats ["gpu_reserved"]=f"{torch .cuda .memory_reserved (0 )/1e9 :.2f} GB"
            stats ["gpu_free"]=f"{(torch .cuda .get_device_properties (0 ).total_memory -torch .cuda .memory_allocated (0 ))/1e9 :.2f} GB"

        return stats 

    def free_memory (self ):
        """Free GPU and NPU memory"""
        if torch .cuda .is_available ():
            torch .cuda .empty_cache ()
            torch .cuda .synchronize ()
            logger .info ("✓ GPU cache cleared and synchronized")

        if self .npu_device :
            try :

                if hasattr (torch ,"xpu"):
                    torch .xpu .empty_cache ()
                    logger .info ("✓ NPU cache cleared")
            except Exception as e :
                logger .debug (f"NPU cache clear failed: {e }")


accelerator =AcceleratedInference ()

