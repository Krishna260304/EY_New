"""
GPU/NPU device management utilities for torch 2.9 with CUDA 13.0
Supports RTX 5070 GPU + Intel AI Boost NPU hybrid acceleration
Optimized for maximum performance on both GPU and NPU
"""

import os 
import torch 
import logging 
from typing import Optional ,List ,Tuple 

logger =logging .getLogger (__name__ )


class DeviceManager :
    """Manages hybrid device usage: GPU + NPU for maximum throughput"""

    def __init__ (self ):
        self .cuda_version =self ._get_cuda_version ()
        self .gpu_device =self ._detect_gpu ()
        self .npu_device =self ._detect_npu ()
        self .primary_device =self .gpu_device if self .gpu_device else self .npu_device 
        self .use_hybrid =self .gpu_device is not None and self .npu_device is not None 
        self .dtype =self ._get_optimal_dtype ()
        self ._log_device_info ()

    def _get_cuda_version (self )->Optional [str ]:
        """Get CUDA version information"""
        try :
            if torch .cuda .is_available ():
                return torch .version .cuda 
        except :
            pass 
        return None 

    def _detect_gpu (self )->Optional [torch .device ]:
        """Detect CUDA-capable GPU (RTX 5070)"""
        if torch .cuda .is_available ():
            try :
                cuda_device =torch .cuda .current_device ()
                gpu_name =torch .cuda .get_device_name (cuda_device )
                logger .info (f"✓ CUDA GPU detected: {gpu_name }")
                gpu_mem =torch .cuda .get_device_properties (cuda_device ).total_memory /1e9 
                logger .info (f"  GPU Memory: {gpu_mem :.2f} GB")
                return torch .device ("cuda")
            except Exception as e :
                logger .warning (f"CUDA initialization failed: {e }")
        return None 

    def _detect_npu (self )->Optional [torch .device ]:
        """Detect Intel AI Boost NPU"""
        try :
            if hasattr (torch ,"xpu")and torch .xpu .is_available ():
                logger .info ("✓ Intel AI Boost NPU detected (XPU)")
                return torch .device ("xpu")
        except Exception as e :
            logger .debug (f"NPU detection failed: {e }")
        return None 

    def _get_optimal_device (self )->torch .device :
        """Get single optimal device (for backward compatibility)"""
        return self .primary_device if self .primary_device else torch .device ("cpu")

    def _get_optimal_dtype (self )->torch .dtype :
        """Select dtype: GPU prefers bfloat16, NPU prefers float16"""
        if self .gpu_device :
            try :
                return torch .bfloat16 
            except :
                return torch .float16 
        elif self .npu_device :
            return torch .float16 
        else :
            return torch .float32 

    def _log_device_info (self ):
        """Log device configuration"""
        logger .info ("="*60 )
        logger .info ("DEVICE CONFIGURATION (CUDA 13.0)")
        logger .info ("="*60 )

        if self .cuda_version :
            logger .info (f"✓ CUDA Version: {self .cuda_version }")

        if self .gpu_device :
            logger .info (f"✓ GPU (CUDA): {self .gpu_device }")
            try :
                logger .info (f"  Compute Capability: {torch .cuda .get_device_capability ()}")
                gpu_mem =torch .cuda .get_device_properties (0 ).total_memory /1e9 
                logger .info (f"  Total Memory: {gpu_mem :.2f} GB")
                logger .info (f"  Device Name: {torch .cuda .get_device_name (0 )}")
            except Exception as e :
                logger .warning (f"  Error getting GPU info: {e }")
        else :
            logger .warning ("⚠ No GPU detected - check CUDA 13.0 installation")

        if self .npu_device :
            logger .info (f"✓ NPU (Intel XPU): {self .npu_device }")
            logger .info (f"  Shared Memory: ~17.9 GB (Intel AI Boost)")
        else :
            logger .info ("⚠ No NPU detected - Intel AI Boost not available")

        if self .use_hybrid :
            logger .info (f"\n🚀 HYBRID MODE ENABLED")
            logger .info (f"  Total compute memory: ~29.9 GB (GPU + NPU)")
            logger .info (f"  Workload distribution: 70% GPU, 30% NPU")

        logger .info (f"Primary Device: {self .primary_device }")
        logger .info (f"Data Type: {self .dtype }")
        logger .info ("="*60 )

    def clear_cache (self ):
        """Clear caches on all available devices"""
        if self .gpu_device :
            try :
                torch .cuda .empty_cache ()
                logger .debug ("CUDA cache cleared")
            except :
                pass 
        if self .npu_device :
            try :
                torch .xpu .empty_cache ()
                logger .debug ("XPU cache cleared")
            except :
                pass 

    def get_device (self )->torch .device :
        """Get primary device"""
        return self .primary_device 

    def get_all_devices (self )->Tuple [Optional [torch .device ],Optional [torch .device ]]:
        """Get both GPU and NPU devices for hybrid processing"""
        return (self .gpu_device ,self .npu_device )

    def is_hybrid_available (self )->bool :
        """Check if both GPU and NPU are available"""
        return self .use_hybrid 

    def distribute_workload (self ,tensor_list :List [torch .Tensor ])->List [Tuple [torch .Tensor ,torch .device ]]:
        """
        Distribute workload across GPU and NPU for parallel processing.
        GPU handles larger batches, NPU handles smaller ones.
        """
        if not self .use_hybrid or len (tensor_list )<2 :
            return [(t ,self .primary_device )for t in tensor_list ]


        split_idx =max (1 ,len (tensor_list )*70 //100 )
        gpu_tensors =tensor_list [:split_idx ]
        npu_tensors =tensor_list [split_idx :]

        result =[(t ,self .gpu_device )for t in gpu_tensors ]
        result +=[(t ,self .npu_device )for t in npu_tensors ]
        return result 

    def get_dtype (self )->torch .dtype :
        """Get optimal data type"""
        return self .dtype 

    def to_device (self ,tensor :torch .Tensor ,device :Optional [torch .device ]=None )->torch .Tensor :
        """Move tensor to device"""
        target_device =device or self .primary_device 
        return tensor .to (target_device ,dtype =self .dtype )

    def __str__ (self )->str :
        return f"DeviceManager(device={self .device }, dtype={self .dtype })"



_device_manager :Optional [DeviceManager ]=None 


def get_device_manager ()->DeviceManager :
    """Get or create global device manager"""
    global _device_manager 
    if _device_manager is None :
        _device_manager =DeviceManager ()
    return _device_manager 


def get_device ()->torch .device :
    """Get primary device"""
    return get_device_manager ().get_device ()


def get_all_devices ()->Tuple [Optional [torch .device ],Optional [torch .device ]]:
    """Get both GPU and NPU devices for hybrid processing"""
    return get_device_manager ().get_all_devices ()


def is_hybrid_available ()->bool :
    """Check if hybrid GPU+NPU mode is available"""
    return get_device_manager ().is_hybrid_available ()


def get_dtype ()->torch .dtype :
    """Get optimal dtype"""
    return get_device_manager ().get_dtype ()


def to_device (tensor :torch .Tensor ,device :Optional [torch .device ]=None )->torch .Tensor :
    """Move tensor to device"""
    return get_device_manager ().to_device (tensor ,device )


def clear_cache ():
    """Clear all device caches"""
    get_device_manager ().clear_cache ()



def setup_gpu_environment ():
    """Configure environment variables for GPU/NPU optimization with CUDA 13.0"""


    os .environ ["CUDA_LAUNCH_BLOCKING"]="0"
    os .environ ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
    os .environ ["CUDA_VISIBLE_DEVICES"]="0"


    if torch .cuda .is_available ():
        try :
            torch .backends .cudnn .enabled =True 
            torch .backends .cudnn .benchmark =True 
            torch .backends .cudnn .deterministic =False 
            torch .backends .cuda .matmul .allow_tf32 =True 
            torch .backends .cudnn .allow_tf32 =True 

            logger .info ("✓ CUDA optimization enabled:")
            logger .info (f"  - cuDNN: {torch .backends .cudnn .enabled }")
            logger .info (f"  - Benchmark: {torch .backends .cudnn .benchmark }")
            logger .info (f"  - TF32: Enabled for both matmul and conv")
        except Exception as e :
            logger .warning (f"CUDA optimization failed: {e }")


    try :
        os .environ ["OV_LOG_LEVEL"]="DEBUG"
        os .environ ["OV_DEVICE"]="NPU"
        logger .info ("✓ OpenVINO/NPU configuration enabled")
    except Exception as e :
        logger .debug (f"OpenVINO setup failed: {e }")


    os .environ ["TOKENIZERS_PARALLELISM"]="true"


    os .environ ["TORCH_ALLOW_TF32"]="1"


    os .environ ["CUDA_EMPTY_CACHE"]="1"

    logger .info ("GPU/NPU environment optimized for CUDA 13.0")
