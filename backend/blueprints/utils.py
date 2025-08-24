from pathlib import Path
from datetime import datetime
import shutil, os

def timestamp():
    return datetime.now().strftime("%Y%m%d-%H%M%S")

def ensure_inside(base_dir: str, target_path: str) -> str:
    base = Path(base_dir).resolve()
    tgt  = Path(target_path).resolve()
    if os.path.commonpath([str(base), str(tgt)]) != str(base):
        raise ValueError("Caminho fora do diretório de dados")
    return str(tgt)

def list_data_files(data_dir: str, query: str | None = None):
    p = Path(data_dir)
    items = []
    if not p.exists():
        return items
    for f in sorted(p.iterdir(), key=lambda x: x.name.lower()):
        if f.is_file():
            if query and query.lower() not in f.name.lower():
                continue
            items.append({"name": f.name, "path": str(f)})
    return items

def backup_file_for(src_path: str, backup_root: str):
    src = Path(src_path)
    per_file_dir = Path(backup_root) / src.name
    per_file_dir.mkdir(parents=True, exist_ok=True)
    dest = per_file_dir / f"{src.name}.{timestamp()}.bak"
    shutil.copy2(src, dest)
    return str(dest)

def list_backups_for(backup_root: str, base_name: str):
    d = Path(backup_root) / base_name
    if not d.exists():
        return []
    return sorted([str(x) for x in d.glob(f"{base_name}.*.bak")], reverse=True)

def safe_write_text(path, content):
    normalized = content.replace("\r\n", "\n").replace("\r", "\n")
    tmp = Path(str(path) + ".tmp")
    tmp.write_text(normalized, encoding="utf-8", newline="\n")
    os.replace(tmp, path)
