"""
硬件服务测试
"""
import pytest
from backend.services.hardware_service import HardwareService
from pathlib import Path


@pytest.fixture
def hardware_service():
    return HardwareService()


def test_get_hardware_info(hardware_service):
    """测试获取硬件信息"""
    info = hardware_service.get_hardware_info()
    assert 'gpu' in info
    assert 'cpu' in info
    assert 'memory' in info


def test_estimate_hardware_pressure(hardware_service):
    """测试硬件压力预估"""
    estimate = hardware_service.estimate_hardware_pressure(
        model_size_gb=2.0,
        batch_size=1,
        precision='fp16'
    )
    assert 'feasible' in estimate
    assert 'estimated_vram_gb' in estimate
    assert 'estimated_time_seconds' in estimate


def test_get_optimization_config(hardware_service):
    """测试获取优化配置"""
    config = hardware_service.get_optimization_config(model_size_gb=2.0)
    assert 'precision' in config
    assert 'batch_size' in config
    assert 'use_gpu' in config

