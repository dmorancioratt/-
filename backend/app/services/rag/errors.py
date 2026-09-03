"""RAG 模块自定义异常。"""


class RagError(Exception):
    """RAG 模块所有异常的基类。"""


class RagInitError(RagError):
    """模型加载失败、索引构建失败等初始化阶段错误。"""


class RagEmptyError(RagError):
    """检索无结果（warn 而非 500）。"""


class RagNotIndexedError(RagError):
    """索引文件不存在，调用方应触发自动重建。"""