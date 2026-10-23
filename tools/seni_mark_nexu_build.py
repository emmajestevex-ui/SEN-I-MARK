#!/usr/bin/env python3
"""Prepare ONLY an iOS app built from Nexu-lite, branded for SEN$I MARK.

Never modifies the checkout or other GitHub repositories. No Supabase SQL or
admin website is copied from Nexu-lite. Build output is isolated in --output.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

BRAND = 'SEN$I MARK'
SUPABASE_URL = 'https://zkprqwgeagqireqrrhei.supabase.co'
PUBLISHABLE_KEY = 'sb_publishable_tQ88K1eydtR-7JBgTfMglQ_J55QtO65'
BUCKET = 'seni-mark-content'
TIKTOK = 'https://www.tiktok.com/@imarkzz20?_r=1&_t=ZS-9AkqsBtfFuW'
BUNDLE = 'com.apple.mobile.MobileHouseArrest'
def must_replace(source: str, old: str, new: str, filename: str) -> str:
    if old not in source:
        raise RuntimeError(f'Base Nexu-lite cambió; falta {old!r} en {filename}. Deteniendo para no producir IPA incorrecta.')
    return source.replace(old, new)


def save(path: Path, content: str) -> None:
    path.write_text(content, encoding='utf-8', newline='\n')


def prepare(base: Path, target: Path, branding: Path) -> None:
    base = base.resolve(strict=True)
    branding = branding.resolve(strict=True)
    target = target.resolve()
    if target == base or base in target.parents or branding in target.parents:
        raise RuntimeError('No se puede generar dentro de la base ni de los recursos originales.')
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)

    # Nexu-lite is the source of the IPA. Exclude GitHub, web admin, SQL and
    # prebuilt archives: the SEN-I-MARK website/database must remain intact.
    excluded = {'.git', '.github', 'admin', 'supabase', 'node_modules', '.build',
                'DerivedData', 'greeg_app_source.zip'}
    for item in base.iterdir():
        if item.name in excluded or item.name.startswith('.'):
            continue
        dest = target / item.name
        if item.is_symlink():
            raise RuntimeError(f'Enlace inesperado en base: {item.name}')
        if item.is_dir():
            shutil.copytree(item, dest)
        elif item.is_file():
            shutil.copy2(item, dest)

    app = target / 'ThreeOneOSFive/App.swift'
    main = target / 'ThreeOneOSFive/ContentView.swift'
    theme = target / 'ThreeOneOSFive/views/DesignSystem.swift'
    info = target / 'ThreeOneOSFive/Info.plist'
    pbx = target / 'ThreeOneOSFive.xcodeproj/project.pbxproj'
    sync = target / 'ThreeOneOSFive/helpers/RemoteContentSyncService.swift'
    toolbar = target / 'ThreeOneOSFive/views/RepositoryMarketplaceView.swift'
    for p in [app,main,theme,info,pbx,sync]:
        if not p.is_file():
            raise RuntimeError(f'Falta un archivo esencial de Nexu-lite: {p.relative_to(target)}')

    a = app.read_text(encoding='utf-8-sig')
    a = must_replace(a,'https://snatmksqzmthkusihzde.supabase.co',SUPABASE_URL,app.name)
    a = must_replace(a,'sb_publishable_WxzuOAgfakLayfoiXfbb4A_Zxaos32q',PUBLISHABLE_KEY,app.name)
    # Separate local license storage so apps cannot share a cached unlock.
    a = a.replace('nexu.license.', 'senimark.license.')
    a = a.replace('NEXU ELITE', BRAND).replace('nexu elite', BRAND)
    a = a.replace('NEXU-ABCD-EF12-3456','SENIMARK-ABCD-EF12-3456')
    # Swift App struct name may change; no other types/model names are modified.
    a = must_replace(a,'struct NexuEliteApp: App','struct SeniMarkApp: App',app.name)
    save(app,a)

    # The Nexu-lite navigation already contains exactly Inicio and Archivos.
    s = main.read_text(encoding='utf-8-sig')
    if 'NexuHomeView' not in s or 'NexuPatchLibraryView' not in s:
        raise RuntimeError('La pantalla de Nexu-lite cambió. No crear una navegación incorrecta.')
    if 'systemImage: "gearshape"' in s[:3500] or '.tabItem { CompactTabLabel(title: "Instalación"' in s:
        raise RuntimeError('La base tiene una pestaña inesperada de Configuración o Instalación.')
    s = s.replace('NEXU ELITE',BRAND).replace('nexu elite',BRAND)
    s = s.replace('Centro NEXU','Centro SEN$I MARK').replace('Archivo NEXU','Archivo SEN$I MARK')
    needle = '                    updatesCard\n'
    tik_tok = (
        '                    Link(destination: URL(string: "'+TIKTOK+'")!) {\n'
        '                        HStack(spacing: 9) {\n'
        '                            Image(systemName: "play.rectangle.fill")\n'
        '                            Text("TikTok · @imarkzz20")\n'
        '                            Spacer()\n'
        '                            Image(systemName: "arrow.up.right")\n'
        '                        }\n'
        '                        .font(.subheadline.weight(.semibold))\n'
        '                        .padding(14)\n'
        '                        .foregroundStyle(.white)\n'
        '                        .background(AppTheme.accent.opacity(0.24), in: RoundedRectangle(cornerRadius: 14))\n'
        '                    }\n'
        '                    .accessibilityLabel("Visitar TikTok de SEN$I MARK")\n'
    )
    s = must_replace(s,needle,needle+tik_tok,main.name)
    save(main,s)

    # Reuse Nexu-lite's red/black palette but use the spider logo in both
    # the launcher icon and visible AppLogo rather than the default SF symbol.
    d = theme.read_text(encoding='utf-8-sig')
    d = must_replace(d,'if let icon = UIImage(named: "AppIcon60x60")',
                     'if let icon = UIImage(named: "SeniMarkLogo")\n                ?? UIImage(named: "AppIcon60x60")',theme.name)
    save(theme,d)

    # Remove visible settings gear from legacy toolbar (if that screen is ever
    # opened). Keep the log utility; do not touch installation/sync mechanisms.
    if toolbar.is_file():
        t = toolbar.read_text(encoding='utf-8-sig')
        legacy = """            Menu {
                Button(action: onOpenSettings) {
                    Label(
                        language.text("settings.title"),
                        systemImage: "gearshape"
                    )
                }
                Button(action: onOpenLogs) {
                    Label(
                        language.text("accessibility.open_logs"),
                        systemImage: "apple.terminal"
                    )
                }
            } label: {
                Image(systemName: "gearshape")
            }
            .accessibilityLabel(language.text("accessibility.open_settings"))"""
        replacement = """            Button(action: onOpenLogs) {
                Image(systemName: "apple.terminal")
            }
            .accessibilityLabel(language.text("accessibility.open_logs"))"""
        if legacy in t:
            t = t.replace(legacy,replacement)
            save(toolbar,t)

    syn = sync.read_text(encoding='utf-8-sig')
    syn = must_replace(syn,'/storage/v1/object/nexu-elite-content/','/storage/v1/object/seni-mark-content/',sync.name)
    syn = syn.replace('NEXU ELITE',BRAND)
    syn = syn.replace('nexu.license.', 'senimark.license.')
    syn = syn.replace('NEXURemoteContent','SeniMarkRemoteContent')
    save(sync,syn)

    # Preserve Swift type names e.g. NexuHomeView, to avoid breaking references.
    # Change only visible strings/preferences in the rest of the iOS source.
    for p in (target/'ThreeOneOSFive').rglob('*'):
        if not p.is_file() or p.suffix.lower() not in {'.swift','.strings','.plist'}:
            continue
        if p in {app,main,theme,info,sync}:
            continue
        try:
            original = p.read_text(encoding='utf-8-sig')
        except UnicodeError:
            continue
        changed = original.replace('NEXU ELITE',BRAND).replace('nexu elite',BRAND)
        changed = changed.replace('https://snatmksqzmthkusihzde.supabase.co',SUPABASE_URL)
        changed = changed.replace('sb_publishable_WxzuOAgfakLayfoiXfbb4A_Zxaos32q',PUBLISHABLE_KEY)
        changed = changed.replace('nexu.license.', 'senimark.license.')
        if changed != original:
            save(p,changed)

    plist = info.read_text(encoding='utf-8-sig')
    plist = plist.replace('nexu elite',BRAND).replace('NEXU ELITE',BRAND)
    for k in ('CFBundleDisplayName','CFBundleName'):
        reg = r'(<key>'+k+r'</key>\s*<string>).*?(</string>)'
        plist, n = re.subn(reg, lambda m:m.group(1)+BRAND+m.group(2),plist,count=1,flags=re.S)
        if n!=1: raise RuntimeError('No encontré '+k+' en Info.plist')
    plist = re.sub(r'(<key>CFBundleIdentifier</key>\s*<string>).*?(</string>)',
                   lambda m:m.group(1)+BUNDLE+m.group(2),plist,count=1,flags=re.S)
    ET.fromstring(plist)
    save(info,plist)
    # The Xcode project has two configurations. Update both.
    project = pbx.read_text(encoding='utf-8-sig')
    project, count=re.subn(r'(PRODUCT_BUNDLE_IDENTIFIER = )[^;]+;',
                          lambda m:m.group(1)+'"'+BUNDLE+'";',project)
    if count<2: raise RuntimeError('No se encontraron ambos bundle identifiers en Xcode')
    project, count=re.subn(r'(INFOPLIST_KEY_CFBundleDisplayName = )[^;]+;',
                          lambda m:m.group(1)+'"'+BRAND+'";',project)
    if count<2: raise RuntimeError('No se encontraron ambos nombres en Xcode')
    save(pbx,project)

    asset_dir=target/'ThreeOneOSFive/Assets.xcassets'
    icon=asset_dir/'AppIcon.appiconset/AppIcon-1024.png'
    logo=asset_dir/'SeniMarkLogo.imageset/SeniMarkLogo.png'
    icon.parent.mkdir(parents=True,exist_ok=True)
    logo.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(branding/'AppIcon-1024.png',icon)
    shutil.copy2(branding/'SeniMarkLogo.png',logo)
    (logo.parent/'Contents.json').write_text(json.dumps({
        'images':[{'filename':'SeniMarkLogo.png','idiom':'universal'}],
        'info':{'author':'xcode','version':1}
    },indent=2)+'\n',encoding='utf-8')

    # Never inherit an incompatible license URL/publishable key.
    verify(target)
    print('SEN$I MARK desde Nexu-lite: verificación estática satisfactoria')


def verify(target: Path) -> None:
    app = (target/'ThreeOneOSFive/App.swift').read_text(encoding='utf-8')
    main = (target/'ThreeOneOSFive/ContentView.swift').read_text(encoding='utf-8')
    syn = (target/'ThreeOneOSFive/helpers/RemoteContentSyncService.swift').read_text(encoding='utf-8')
    project = (target/'ThreeOneOSFive.xcodeproj/project.pbxproj').read_text(encoding='utf-8')
    plist = (target/'ThreeOneOSFive/Info.plist').read_text(encoding='utf-8')
    assert 'struct SeniMarkApp: App' in app
    assert SUPABASE_URL in app and PUBLISHABLE_KEY in app
    assert 'snatmksqzmthkusihzde' not in app
    assert TIKTOK in main
    assert 'Text("SEN$I MARK")' in main
    assert main.count('.tabItem { CompactTabLabel(')==2, 'La interfaz no contiene exactamente Inicio/Archivos'
    assert '.tabItem { CompactTabLabel(title: "Inicio"' in main
    assert '.tabItem { CompactTabLabel(title: "Archivos"' in main
    assert '/storage/v1/object/seni-mark-content/' in syn
    assert BUNDLE in project and BRAND in project
    assert (target/'ThreeOneOSFive/Assets.xcassets/AppIcon.appiconset/AppIcon-1024.png').is_file()
    assert (target/'ThreeOneOSFive/Assets.xcassets/SeniMarkLogo.imageset/SeniMarkLogo.png').is_file()
    assert ET.fromstring(plist) is not None
    assert not (target/'admin').exists(), 'No debe copiarse la página admin desde Nexu-lite'
    assert not (target/'supabase').exists(), 'No debe copiarse el SQL desde Nexu-lite'


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--base',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--branding',required=True,type=Path)
    args=parser.parse_args()
    prepare(args.base,args.output,args.branding)
