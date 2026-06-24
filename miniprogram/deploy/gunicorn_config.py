"""家庭私厨 — Gunicorn 配置"""
import multiprocessing

bind = "127.0.0.1:5000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
timeout = 120

accesslog = "/var/log/caipu/access.log"
errorlog = "/var/log/caipu/error.log"
loglevel = "info"

proc_name = "caipu-api"
graceful_timeout = 10
max_requests = 1000
max_requests_jitter = 100
