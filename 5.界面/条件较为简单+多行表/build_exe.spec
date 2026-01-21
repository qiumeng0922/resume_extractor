# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller 配置文件 - AI简历初筛系统
用于打包成Windows EXE可执行文件
"""

import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(SPEC))

# 收集所有需要包含的数据文件
datas = [
    ('data', 'data'),  # 包含data目录及其所有文件
    ('index.html', '.'),  # 包含前端HTML文件
    ('config.py', '.'),  # 包含配置文件
]

# 收集所有Python子模块（确保所有模块都被包含）
hiddenimports = [
    # FastAPI相关
    'fastapi',
    'fastapi.middleware.cors',
    'fastapi.responses',
    'fastapi.staticfiles',
    'uvicorn',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.loops.uvloop',
    'uvicorn.loops.asyncio',
    
    # Excel处理
    'openpyxl',
    'openpyxl.cell',
    'openpyxl.workbook',
    'openpyxl.worksheet',
    'pandas',
    'numpy',
    
    # 数据处理
    'json',
    'tempfile',
    'shutil',
    'asyncio',
    'threading',
    'webbrowser',
    
    # 项目模块
    'parsers.detect_merged_cells_with_accuracy',
    'parsers.detect_merged_cells_with_accuracy_position_adjust',
    'parsers.clean_external',
    'core.screener',
    'core.models',
    'core.toolkit',
    'managers.llm_manager',
    'utils.logger_config',
    'utils.data_loader',
    'utils.calculator',
    'utils.major_library',
    'filters.age',
    'filters.base',
    'filters.education',
    'filters.major',
    'filters.performance',
    'filters.political_status',
    'filters.title',
    'filters.work_experience',
    'filters.work_years',
    'matchers.llm_matcher',
    'matchers.rule_matcher',
    'extractors.requirement_extractor',
    'extractors.resume_extractor',
    'exporters.result_exporter',
    
    # LangChain相关
    'langchain_openai',
    'langchain_openai.chat_models',
    'langchain_core',
    'langchain_core.language_models',
    'langchain_core.messages',
    'langchain_core.outputs',
    'langchain_core.runnables',
    
    # FastAPI核心依赖
    'starlette',
    'starlette.applications',
    'starlette.middleware',
    'starlette.routing',
    'starlette.responses',
    'pydantic',
    'pydantic.fields',
    'pydantic.main',
    'anyio',
    'anyio.streams',
    'sniffio',
    'httptools',
    'websockets',
    'websockets.server',
    'websockets.client',
    
    # FastAPI文件上传依赖
    'python_multipart',
    'multipart',
    
    # Pydantic额外依赖
    'typing_extensions',
    'email_validator',
    
    # HTTP相关
    'httpx',
    'httpx._client',
    'httpx._transports',
    'requests',  # 可能被某些库使用
    'aiohttp',  # 异步HTTP客户端
    'aiohttp.client',
    'aiohttp.connector',
    'idna',
    'h11',
    'h2',
    'certifi',
    
    # 其他可能需要的依赖
    'click',
    'rich',
    'tenacity',  # langchain可能使用
    'yarl',  # aiohttp依赖
    'multidict',  # aiohttp依赖
    'async_timeout',  # aiohttp依赖
]

# 收集所有子模块
try:
    hiddenimports.extend(collect_submodules('fastapi'))
    hiddenimports.extend(collect_submodules('uvicorn'))
    hiddenimports.extend(collect_submodules('openpyxl'))
    hiddenimports.extend(collect_submodules('pandas'))
    hiddenimports.extend(collect_submodules('starlette'))  # FastAPI依赖
    hiddenimports.extend(collect_submodules('pydantic'))  # FastAPI依赖
    hiddenimports.extend(collect_submodules('anyio'))  # FastAPI依赖
    hiddenimports.extend(collect_submodules('sniffio'))  # FastAPI依赖
    hiddenimports.extend(collect_submodules('httptools'))  # uvicorn依赖
    hiddenimports.extend(collect_submodules('websockets'))  # uvicorn依赖
    hiddenimports.extend(collect_submodules('langchain_openai'))  # LangChain OpenAI
    hiddenimports.extend(collect_submodules('langchain_core'))  # LangChain核心
except:
    pass

a = Analysis(
    ['backend.py'],
    pathex=[current_dir],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',  # 排除不需要的库以减小体积
        'tkinter',
        'PyQt5',
        'PyQt6',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AI简历初筛系统',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # 使用UPX压缩（如果可用）
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 显示控制台窗口（方便查看日志）
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可以添加图标文件路径，例如: icon='icon.ico'
)
