from __future__ import annotations

import json
from pathlib import Path
import shutil
import tarfile


ROLE_ALIASES = {
    "ref_seq": "harmonization_ref_seq",
    "ref_infer_vcf": "harmonization_ref_infer_vcf",
    "ref_rsid_tsv": "assign_rsid_tsv",
    "ref_rsid_vcf": "assign_rsid_vcf",
}
INDEX_NAME_ALIASES = {
    "ref_infer_vcf_tbi": "ref_infer_vcf",
    "ref_rsid_vcf_tbi": "ref_rsid_vcf",
}


def load_manifest(manifest_path: str | Path) -> dict[str, object]:
    return json.loads(Path(manifest_path).read_text(encoding="utf-8"))


def extract_reference_bundle(bundle_path: str | Path, extract_root: str | Path) -> Path:
    extract_dir = Path(extract_root)
    extract_dir.mkdir(parents=True, exist_ok=True)
    with tarfile.open(bundle_path, "r:gz") as archive:
        archive.extractall(extract_dir)
    return extract_dir


def _index_entries(resources: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    indexed: dict[str, dict[str, object]] = {}
    for resource in resources:
        name = resource.get("name")
        role = resource.get("role")
        if isinstance(name, str):
            indexed[name] = resource
        if isinstance(role, str):
            indexed[role] = resource
    return indexed


def ensure_vcf_index_pairings(extract_root: Path, resources: list[dict[str, object]]) -> None:
    indexed = _index_entries(resources)
    for index_name, vcf_name in INDEX_NAME_ALIASES.items():
        if index_name not in indexed or vcf_name not in indexed:
            continue
        index_rel = indexed[index_name].get("bundle_path")
        vcf_rel = indexed[vcf_name].get("bundle_path")
        if not isinstance(index_rel, str) or not isinstance(vcf_rel, str):
            continue

        source_index = extract_root / "references" / index_rel
        vcf_path = extract_root / "references" / vcf_rel
        if not source_index.exists() or not vcf_path.exists():
            continue

        target_index = Path(f"{vcf_path}.tbi")
        if not target_index.exists():
            shutil.copy2(source_index, target_index)


def resolve_reference_paths(
    bundle_path: str | Path,
    manifest_path: str | Path,
    extract_root: str | Path,
) -> dict[str, str]:
    manifest = load_manifest(manifest_path)
    resources = manifest.get("resources", [])
    if not isinstance(resources, list):
        raise ValueError("Reference bundle manifest does not contain a valid resources list.")

    extracted_root = extract_reference_bundle(bundle_path, extract_root)
    ensure_vcf_index_pairings(extracted_root, resources)

    resolved: dict[str, str] = {}
    for resource in resources:
        name = resource.get("name")
        role = resource.get("role")
        bundle_rel = resource.get("bundle_path")
        if not isinstance(bundle_rel, str):
            continue
        real_path = extracted_root / "references" / bundle_rel
        if not real_path.exists():
            continue

        if isinstance(role, str) and role in ROLE_ALIASES.values() and role not in resolved:
            resolved[role] = str(real_path)
        if isinstance(name, str) and name in ROLE_ALIASES:
            resolved[ROLE_ALIASES[name]] = str(real_path)

    return resolved
