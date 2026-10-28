"""Small, explicit provenance sidecars for published analysis results."""
import hashlib
import json
from pathlib import Path
import platform
import networkx
import numpy
import scipy

ROOT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def metadata_for(data_path, source_files, model_version):
    return {
        'schema_version': 1,
        'model_version': model_version,
        'dataset_file': Path(data_path).name,
        'dataset_sha256': digest(data_path),
        'source_sha256': {name: digest(ROOT/name) for name in source_files},
        'runtime': {'python': platform.python_version(), 'networkx': networkx.__version__,
                    'numpy': numpy.__version__, 'scipy': scipy.__version__},
    }


def save_manifest(path, result_path, metadata):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {**metadata, 'result_file': Path(result_path).name, 'result_sha256': digest(result_path)}
    target.write_text(json.dumps(payload, indent=2)+'\n')
