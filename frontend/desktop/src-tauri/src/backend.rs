// 后端服务管理模块
use std::process::{Command, Child};
use std::path::PathBuf;
use tauri::State;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BackendStatus {
    pub running: bool,
    pub pid: Option<u32>,
    pub port: u16,
}

pub struct BackendManager {
    process: Option<Child>,
    port: u16,
}

impl BackendManager {
    pub fn new(port: u16) -> Self {
        Self {
            process: None,
            port,
        }
    }

    pub fn start(&mut self, backend_path: PathBuf) -> Result<(), String> {
        if self.process.is_some() {
            return Err("Backend is already running".to_string());
        }

        // 尝试使用 Python 虚拟环境
        let python_cmd = if cfg!(target_os = "windows") {
            "python"
        } else {
            "python3"
        };

        let mut cmd = Command::new(python_cmd);
        cmd.arg(backend_path.join("main.py"));
        cmd.current_dir(&backend_path);
        cmd.env("PORT", self.port.to_string());
        cmd.stdout(std::process::Stdio::null());
        cmd.stderr(std::process::Stdio::null());

        match cmd.spawn() {
            Ok(child) => {
                self.process = Some(child);
                Ok(())
            }
            Err(e) => Err(format!("Failed to start backend: {}", e)),
        }
    }

    pub fn stop(&mut self) -> Result<(), String> {
        if let Some(mut child) = self.process.take() {
            #[cfg(unix)]
            {
                use std::os::unix::process::CommandExt;
                let _ = child.kill();
            }
            #[cfg(windows)]
            {
                let _ = child.kill();
            }
            let _ = child.wait();
            Ok(())
        } else {
            Err("Backend is not running".to_string())
        }
    }

    pub fn status(&self) -> BackendStatus {
        BackendStatus {
            running: self.process.is_some(),
            pid: self.process.as_ref().map(|p| p.id()),
            port: self.port,
        }
    }
}

#[tauri::command]
pub async fn start_backend(
    backend_path: String,
    manager: State<'_, tauri::async_runtime::Mutex<BackendManager>>,
) -> Result<BackendStatus, String> {
    let mut mgr = manager.lock().await;
    mgr.start(PathBuf::from(backend_path))?;
    Ok(mgr.status())
}

#[tauri::command]
pub async fn stop_backend(
    manager: State<'_, tauri::async_runtime::Mutex<BackendManager>>,
) -> Result<(), String> {
    let mut mgr = manager.lock().await;
    mgr.stop()?;
    Ok(())
}

#[tauri::command]
pub async fn get_backend_status(
    manager: State<'_, tauri::async_runtime::Mutex<BackendManager>>,
) -> Result<BackendStatus, String> {
    let mgr = manager.lock().await;
    Ok(mgr.status())
}

