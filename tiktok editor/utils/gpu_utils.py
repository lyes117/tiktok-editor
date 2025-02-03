import torch
import cv2
import multiprocessing

def get_device():
    if torch.cuda.is_available():
        return torch.device('cuda')
    return torch.device('cpu')

def get_optimal_thread_count():
    return multiprocessing.cpu_count()

def frame_to_gpu(frame):
    if torch.cuda.is_available():
        return cv2.cuda_GpuMat(frame)
    return frame

def frame_to_cpu(frame):
    if torch.cuda.is_available() and isinstance(frame, cv2.cuda_GpuMat):
        return frame.download()
    return frame
