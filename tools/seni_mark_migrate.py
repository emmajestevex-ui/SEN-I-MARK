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
IGNORE_DIRS = {'.git','.build','node_modules','Pods','DerivedData'}
OLD_BRANDS = ['GLOBAL IOS','Global IOS','Software Ch3at','SOFTWARE CH3AT','SoftCh3at','Gllyzi','GLLYZI','GLIZZY','GREEG APP','GREEG-APP','GREEG_APP','GREEG','GlobalIOS','GLOBALIOS']
OLD_KEY_PREFIXES = ['GLOBALIOS-','SOFTWARECH3AT-','SOFTCH3AT-','GLYYZI-','GLIZZY-','GREEG-']
APP_ICON = ROOT/'branding'/'AppIcon-1024.png'
LOGO = ROOT/'branding'/'SeniMarkLogo.png'


def clone_files(base: Path):
    if not base.is_dir():
        raise SystemExit(f'La base no existe: {base}')
    for item in list(ROOT.iterdir()):
        if item.name in {'branding','tools','.github','LEEME_PRIMERO_SENI_MARK.txt'}:
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()
    for src in base.iterdir():
        if src.name in IGNORE_DIRS:
            continue
        dst = ROOT/src.name
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)


def replace_all(text: str) -> str:
    text = text.replace('\r\n','\n').replace('\r','\n')
    for b in OLD_BRANDS:
        text = text.replace(b, BRAND)
    for p in OLD_KEY_PREFIXES:
        text = text.replace(p, PREFIX + '-')
    text = re.sub(r'https://[a-z0-9]{20}\.supabase\.co', URL, text)
    text = re.sub(r'sb_publishable_[A-Za-z0-9_\-]+', KEY, text)
    text = re.sub(r'https://www\.tiktok\.com/@[^\s"\']+', TIKTOK, text)
    text = re.sub(r'https://discord\.gg/[^\s"\']+', TIKTOK, text)
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
    sql_dir = ROOT/'supabase'
    sql_dir.mkdir(parents=True, exist_ok=True)
    setup = sql_dir/'setup_all.sql'
    base_sql = setup.read_text(encoding='utf-8-sig') if setup.exists() else '-- setup_all.sql no encontrado en la base; completa este archivo con tu esquema original.\n'
    base_sql = replace_all(base_sql)
    header = f"-- SEN$I MARK - SQL completo\n-- Proyecto: {PROJECT_ID}\n-- URL: {URL}\n-- Publishable key: {KEY}\n\n"
    (sql_dir/'SETUP_SENI_MARK_COMPLETO.sql').write_text(header + base_sql, encoding='utf-8', newline='\n')
    assign = """-- SEN$I MARK - ASIGNAR ADMINISTRADOR\n\nINSERT INTO public.license_admins (user_id, role)\nSELECT id, 'founder'\nFROM auth.users\nWHERE lower(email) = 'CAMBIA_AQUI_TU_EMAIL'\nON CONFLICT (user_id)\nDO UPDATE SET role = EXCLUDED.role;\n\nSELECT u.email, a.role\nFROM public.license_admins a\nJOIN auth.users u ON u.id = a.user_id\nWHERE lower(u.email) = 'CAMBIA_AQUI_TU_EMAIL';\n"""
    (sql_dir/'ASIGNAR_ADMIN_SENI_MARK.sql').write_text(assign, encoding='utf-8', newline='\n')
    CHANGES.extend(['supabase/SETUP_SENI_MARK_COMPLETO.sql','supabase/ASIGNAR_ADMIN_SENI_MARK.sql'])


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
