import logging, os, colorlog, sys

log_directory = 'storage/logs'
log_file = 'main_api.log'

# 確保日誌目錄和檔案存在
if not os.path.exists(log_directory):
    os.makedirs(log_directory)
if not os.path.exists(os.path.join(log_directory, log_file)):
    with open(os.path.join(log_directory, log_file), 'w') as f:
        pass

# 設定第三方函式庫的日誌等級
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

# 建立日誌格式
log_format = "%(log_color)s%(asctime)s - %(name)s - %(filename)s - %(funcName)s - %(levelname)s - %(message)s"
date_format = '%Y-%m-%d %H:%M:%S'

# 確保不重複新增處理器
logger = logging.getLogger("Logger")

if not logger.hasHandlers():
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[
            # 設定檔案處理器
            logging.FileHandler(os.path.join(log_directory, log_file),
                                mode='a'),
            # 設定控制台處理器
            logging.StreamHandler(sys.stderr)
        ])

for handler in logging.getLogger().handlers:
    if isinstance(handler, colorlog.StreamHandler):
        handler.setFormatter(
            colorlog.ColoredFormatter(log_format,
                                      datefmt=date_format,
                                      log_colors={
                                          "DEBUG": "cyan",
                                          "INFO": "green",
                                          "WARNING": "yellow",
                                          "ERROR": "red",
                                          "CRITICAL": "bold_red",
                                      }))
