#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, shutil
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BRAND = 'SEN$I MARK'
PROJECT_ID = 'zkprqwgeagqireqrrhei'
URL = f'https://{PROJECT_ID}.supabase.co'
KEY = 'sb_publishable_tQ88K1eydtR-7JBgTfMglQ_J55QtO65'
PREFIX = 'SENIMARK'
BUNDLE_ID = 'com.senimark.client'
TIKTOK = 'https://www.tiktok.com/@imarkzz20?_r=1&_t=ZS-9AkqsBtfFuW'
CHANGES = []
TEXT_EXTS = {'.swift','.m','.h','.plist','.pbxproj','.js','.html','.css','.json','.md','.sql','.txt','.xml','.yaml','.yml','.sh','.bat'}
IGNORE_DIRS = {'.git','.github','.senimark-base','.build','node_modules','Pods','DerivedData'}
OLD_BRANDS = ['GLOBAL IOS','Global IOS','Software Ch3at','SOFTWARE CH3AT','SoftCh3at','Gllyzi','GLLYZI','GLIZZY','GREEG APP','GREEG-APP','GREEG_APP','GlobalIOS','GLOBALIOS']
OLD_KEY_PREFIXES = ['GLOBALIOS-','SOFTWARECH3AT-','SOFTCH3AT-','GLYYZI-','GLIZZY-','GREEG-']
APP_ICON = ROOT/'branding'/'AppIcon-1024.png'
LOGO = ROOT/'branding'/'SeniMarkLogo.png'


def clone_files(base: Path):
    """Copy the public source tree without destroying the checked-out source or Git.

    GitHub Actions checks out GREEG-APP to ROOT/.senimark-base. Keeping that
    directory is mandatory until the copy has finished. Original workflows are
    deliberately not merged so only SEN$I MARK's workflow can be triggered.
    """
    base = base.resolve()
    if not base.is_dir():
        raise SystemExit(f'La base no existe: {base}')
    if base == ROOT.resolve():
        raise SystemExit('La base debe ser una carpeta distinta del repositorio destino')
    preserved = {
        '.git', '.github', 'tools', 'branding', '.senimark-base',
        'LEEME_PRIMERO_SENI_MARK.txt',
    }
    for item in list(ROOT.iterdir()):
        if item.name in preserved or item.resolve() == base:
            continue
        if item.is_dir() and not item.is_symlink():
            shutil.rmtree(item)
        else:
            item.unlink()
    # This list is materialized before any filesystem mutations.
    for src in list(base.iterdir()):
        if src.name in IGNORE_DIRS or src.name in {'.github', 'branding'}:
            continue
        dst = ROOT / src.name
        if src.name == 'tools' and src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
        elif src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dst)


def replace_all(text: str) -> str:
    text = text.replace('\r\n','\n').replace('\r','\n')
    for b in OLD_BRANDS:
        text = text.replace(b, BRAND)
    # Standalone brand tokens may occur in JavaScript identifiers or SQL names.
    # Use an identifier-safe replacement; display labels are handled above.
    text = text.replace('GREEG_', PREFIX + '_')
    text = re.sub(r'\bGREEG\b', PREFIX, text)
    for p in OLD_KEY_PREFIXES:
        text = text.replace(p, PREFIX + '-')
    text = re.sub(r'https://[a-z0-9]{20}\.supabase\.co', URL, text)
    text = re.sub(r'sb_publishable_[A-Za-z0-9_\-]+', KEY, text)
    text = re.sub(r'https://www\.tiktok\.com/@[^\s"\']+', TIKTOK, text)
    text = re.sub(r'https://discord\.gg/[^\s"\']+', TIKTOK, text)
    text = text.replace('greeg-content', 'seni-mark-content')
    text = text.replace('GreegLogo', 'SeniMarkLogo')
    text = text.replace('greeg-logo.png', 'seni-mark-logo.png')
    text = text.replace('global-ios-logo.png','seni-mark-logo.png').replace('GlobalIOSLogo','SeniMarkLogo')
    text = text.replace('global_ios','seni_mark').replace('GLOBAL_IOS','SENI_MARK').replace('global-ios','seni-mark')
    text = re.sub(r'\b(GLOBALIOS|SOFTWARECH3AT|SOFTCH3AT|GLYYZI|GLIZZY|GREEG)\b', PREFIX, text)
    return text


def update_text_files():
    for p in ROOT.rglob('*'):
        if not p.is_file():
            continue
        if any(part in IGNORE_DIRS for part in p.parts):
            continue
        if p.relative_to(ROOT).as_posix() == 'tools/seni_mark_migrate.py':
            continue
        if p.name == 'Contents.json' and 'Assets.xcassets' in p.parts:
            continue
        if p.suffix.lower() not in TEXT_EXTS:
            continue
        try:
            old = p.read_text(encoding='utf-8-sig')
        except Exception:
            continue
        new = replace_all(old)
        if new != old:
            p.write_text(new, encoding='utf-8', newline='\n')
            CHANGES.append(str(p.relative_to(ROOT)))


def write_logo_targets():
    targets = [
        ROOT/'admin'/'seni-mark-logo.png',
        ROOT/'admin'/'global-ios-logo.png',
        ROOT/'admin'/'gllyzi-logo.png',
        ROOT/'admin'/'greeg-logo.png',
        ROOT/'ThreeOneOSFive'/'Assets.xcassets'/'AppIcon.appiconset'/'AppIcon-1024.png',
        ROOT/'ThreeOneOSFive'/'Assets.xcassets'/'SeniMarkLogo.imageset'/'SeniMarkLogo.png',
        ROOT/'ThreeOneOSFive'/'Assets.xcassets'/'GllyziLogo.imageset'/'GllyziLogo.png',
        ROOT/'ThreeOneOSFive'/'Assets.xcassets'/'GlobalIOSLogo.imageset'/'GlobalIOSLogo.png',
        ROOT/'ThreeOneOSFive'/'Assets.xcassets'/'GreegLogo.imageset'/'GreegLogo.png',
    ]
    for t in targets:
        t.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(APP_ICON if t.name == 'AppIcon-1024.png' else LOGO, t)
        CHANGES.append(str(t.relative_to(ROOT)))
    contents = '{\n  "images" : [\n    {\n      "filename" : "SeniMarkLogo.png",\n      "idiom" : "universal"\n    }\n  ],\n  "info" : {\n    "author" : "xcode",\n    "version" : 1\n  }\n}\n'
    (ROOT/'ThreeOneOSFive'/'Assets.xcassets'/'SeniMarkLogo.imageset'/'Contents.json').write_text(contents, encoding='utf-8')


def patch_info_files():
    plist = ROOT/'ThreeOneOSFive'/'Info.plist'
    if plist.exists():
        txt = plist.read_text(encoding='utf-8-sig')
        txt = re.sub(r'<key>CFBundleDisplayName</key>\s*<string>.*?</string>', '<key>CFBundleDisplayName</key>\n\t<string>SEN$I MARK</string>', txt, flags=re.S)
        txt = re.sub(r'<key>CFBundleName</key>\s*<string>.*?</string>', '<key>CFBundleName</key>\n\t<string>SEN$I MARK</string>', txt, flags=re.S)
        plist.write_text(txt, encoding='utf-8', newline='\n')
        CHANGES.append('ThreeOneOSFive/Info.plist')
    pbx = ROOT/'ThreeOneOSFive.xcodeproj'/'project.pbxproj'
    if pbx.exists():
        txt = pbx.read_text(encoding='utf-8-sig')
        txt = re.sub(r'PRODUCT_BUNDLE_IDENTIFIER = [^;]+;', f'PRODUCT_BUNDLE_IDENTIFIER = {BUNDLE_ID};', txt)
        txt = txt.replace('INFOPLIST_KEY_CFBundleDisplayName = 3105;','INFOPLIST_KEY_CFBundleDisplayName = "SEN$I MARK";')
        pbx.write_text(txt, encoding='utf-8', newline='\n')
        CHANGES.append('ThreeOneOSFive.xcodeproj/project.pbxproj')


def write_sql_files():
    """Build the SQL from real source scripts, omitting old demo credentials.

    The original project has no `supabase/setup_all.sql`. Its real schema is
    split among licenses_setup.sql, remote_content_setup.sql and a patch update.
    """
    sql_dir = ROOT / 'supabase'
    sql_dir.mkdir(parents=True, exist_ok=True)
    sources = [
        'licenses_setup.sql',
        'remote_content_setup.sql',
        'allow_duplicate_remote_patches.sql',
    ]
    sections = []
    for name in sources:
        path = sql_dir / name
        if not path.exists():
            raise AssertionError(f'Falta SQL real de la base GREEG-APP: {path}')
        chunk = path.read_text(encoding='utf-8-sig')
        # Do not grant old project's users founder access on this new project.
        chunk = re.sub(
            r"(?ims)^\s*insert into public\.license_admins\s*\(user_id,\s*role\)\s*"
            r"select id,\s*'founder'\s*from auth\.users\s*where lower\(email\) in\s*"
            r"\(.*?\)\s*on conflict \(user_id\) do update\s*set role = excluded\.role;",
            '\n-- Admin seed omitted intentionally: assign your own verified Auth user later.\n', chunk)
        # Do not transplant the base project's demo access key.
        chunk = re.sub(
            r"(?ims)^\s*insert into public\.licenses\s*\(license_key,\s*label,\s*capabilities,\s*status,\s*is_active\)"
            r"\s*values\s*\(.*?\)\s*on conflict\s*\(license_key\)\s*do update\s*set.*?;",
            '\n-- Demo license seed omitted intentionally.\n', chunk)
        chunk = replace_all(chunk)
        sections.append(f'\n-- ===== {name} =====\n' + chunk.rstrip() + '\n')
    header = (
        f'-- SEN$I MARK - SQL basado en scripts reales de GREEG-APP\n'
        f'-- Nuevo proyecto Supabase: {PROJECT_ID}\n'
        '-- Ejecutar SOLO en la nueva base, revisar antes de ejecutar.\n'
        '-- ADMIN: crear primero el usuario en Authentication > Users.\n'
    )
    (sql_dir / 'SETUP_SENI_MARK_COMPLETO.sql').write_text(
        header + '\n'.join(sections), encoding='utf-8', newline='\n')
    assign = """-- SEN$I MARK: asigna tu usuario existente de Authentication.
-- Reemplaza CAMBIA_AQUI_TU_EMAIL por tu correo y ejecuta DESPUES del setup.
DO $$
DECLARE
  v_email text := 'CAMBIA_AQUI_TU_EMAIL';
  v_id uuid;
BEGIN
  IF v_email = 'CAMBIA_AQUI_TU_EMAIL' THEN
    RAISE EXCEPTION 'Reemplaza CAMBIA_AQUI_TU_EMAIL por tu propio correo en Authentication';
  END IF;
  SELECT id INTO v_id FROM auth.users WHERE lower(email) = lower(trim(v_email));
  IF v_id IS NULL THEN
    RAISE EXCEPTION 'El usuario no existe en Authentication > Users';
  END IF;
  INSERT INTO public.license_admins(user_id, role) VALUES (v_id, 'founder')
  ON CONFLICT (user_id) DO UPDATE SET role = EXCLUDED.role;
END $$;
"""
    (sql_dir / 'ASIGNAR_ADMIN_SENI_MARK.sql').write_text(assign, encoding='utf-8', newline='\n')
    CHANGES.extend(['supabase/SETUP_SENI_MARK_COMPLETO.sql', 'supabase/ASIGNAR_ADMIN_SENI_MARK.sql'])


def write_docs():
    note = f"# SEN$I MARK\n\nProyecto derivado de GREEG-APP con identidad nueva.\n\n- Proyecto Supabase: {PROJECT_ID}\n- URL: {URL}\n- Publishable key: {KEY}\n- TikTok: {TIKTOK}\n- Prefix para keys: {PREFIX}-\n"
    (ROOT/'README.md').write_text(note, encoding='utf-8', newline='\n')
    CHANGES.append('README.md')


def verify():
    required = [
        'branding/AppIcon-1024.png',
        'branding/SeniMarkLogo.png',
        '.github/workflows/seni_mark_release.yml',
        'tools/seni_mark_migrate.py',
        'supabase/SETUP_SENI_MARK_COMPLETO.sql',
        'supabase/ASIGNAR_ADMIN_SENI_MARK.sql',
    ]
    for rel in required:
        if not (ROOT/rel).exists():
            raise AssertionError('Falta ' + rel)
    sql = (ROOT/'supabase/SETUP_SENI_MARK_COMPLETO.sql').read_text(encoding='utf-8')
    assert 'create table if not exists public.licenses' in sql.lower(), 'SQL no incluye tabla licenses'
    assert 'remote_content_files' in sql, 'SQL no incluye funciones de archivos'
    assert 'greeg-content' not in sql.lower(), 'SQL contiene bucket antiguo'
    assert 'ysiemmanuel9@gmail.com' not in sql.lower(), 'SQL contiene admin del proyecto base'
    info = ROOT/'ThreeOneOSFive'/'Info.plist'
    if info.exists():
        ET.fromstring(info.read_text(encoding='utf-8-sig'))
    print('Validación estática: OK. No equivale a compilación real ni a ejecución SQL.')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base')
    ap.add_argument('--verify', action='store_true')
    args = ap.parse_args()
    if args.verify:
        verify()
        return
    if args.base:
        clone_files(Path(args.base))
    update_text_files()
    write_logo_targets()
    patch_info_files()
    write_sql_files()
    write_docs()
    verify()
    print(json.dumps({'changed': CHANGES}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
