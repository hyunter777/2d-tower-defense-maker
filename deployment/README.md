# doc 사이트 배포 계획 (release R1, 2026-11-21)

이 폴더는 **초안**만 둔다. 실제로 활성화된 워크플로는 없다. 제품 저장소(`2d-tower-defense-maker-source`, 비공개)에서는 아무것도 배포되지 않는다.

## 1. 지금 공개되는 경로 (as-is)

| 요소 | 값 |
|---|---|
| 공개 문서·지원 저장소 | `https://github.com/hyunter777/2d-tower-defense-maker` (공개). 문서 전용이며 제품 구현·어셈블리는 없다 |
| 제품 소스 저장소 | `https://github.com/hyunter777/2d-tower-defense-maker-source` (비공개, 이 저장소의 `origin`) |
| 사이트 | `https://hyunter777.github.io/2d-tower-defense-maker/` |
| Pages 게시 소스 | 브랜치 `gh-pages` / 루트(`/`). `gh-pages`에 `.nojekyll` 포함, 811파일 |
| 현재 배포 방법 | 로컬에서 `python scripts/build.py --output site` → `ghp-import -n -p site`로 `gh-pages` push (수동) |
| 문서 소스 반입 | `docs/site/` 내용을 공개 저장소 루트로 복사해 `main`에 commit/push (수동) |
| 워크플로 | 템플릿만 `docs/site/deployment/pages-workflow.yml`로 보관. `.github/workflows`에 올린 적 없음 |

근거:

- `docs/handover.md` 24·26·92행: 소스 저장소 비공개, 공개 저장소는 문서 전용, "배포는 로컬에서 엄격 빌드한 정적 파일을 `gh-pages`로 push", "현재 인증에는 workflow 쓰기 권한이 없어 활성 커스텀 Actions 워크플로 대신 비활성 템플릿을 보관".
- `.work/qa08/docs-publish`(공개 저장소 clone, `main`=`2c3f04b`, `gh-pages`=`cd61bb3`): 루트에 `mkdocs.yml`, `docs/en`, `api-metadata`, `docfx`, `scripts`, `deployment`, `requirements.txt`, `LICENSE`가 있다. 즉 이 저장소의 `docs/site/`가 공개 저장소 루트와 1:1 대응한다(파일 목록 480개 동일, 내용은 영문 가이드 5개가 이 저장소 쪽에서 더 최신).
- `docs/site/README.md`: 같은 절차(엄격 빌드 → `ghp-import -n -p`)와 "워크플로 템플릿은 workflow 쓰기 권한이 있는 관리자용"이라는 설명.

## 2. 제안 (to-be)

### 2.1 워크플로는 공개 문서 저장소에 둔다

- 파일: 공개 저장소 `.github/workflows/pages.yml` ← 이 폴더의 `pages-workflow.yml` 초안.
- 제품(비공개) 저장소에는 배포 워크플로를 두지 않는다. 사이트 산출물·API 메타데이터·가이드는 공개 저장소에만 있고, Pages는 그 저장소의 Pages 기능으로만 게시된다.
- 트리거: `main` push(문서·메타데이터·빌드 입력 경로만) + `workflow_dispatch`.
- 게시 방식: 브랜치 게시(`gh-pages`) 대신 **Actions 게시**(`configure-pages` + `upload-pages-artifact` + `deploy-pages`). 저장소 설정에서 Pages 소스를 "GitHub Actions"로 바꿔야 하며, 이 변경은 lead/사용자만 할 수 있다.
- 이유: `ghp-import` 단계가 사라지고, 빌드 실패가 배포 실패로 이어져 깨진 사이트가 게시되지 않는다. `gh-pages` 브랜치 이력도 더 이상 늘지 않는다. 되돌리려면 소스를 `gh-pages`로 다시 바꾸고 기존 수동 절차를 쓰면 된다(브랜치는 그대로 남겨 둔다).

### 2.2 비공개 소스 → 공개 저장소 소스 이동

1. **기본(권장, 지금 바로 가능): 수동 동기화 유지.** lead가 `docs/site/` 내용을 공개 저장소 `main`에 commit/push한다(현재와 동일). 이 push가 2.1 워크플로를 깨워 빌드·배포까지 자동으로 끝낸다. 즉 자동화 범위는 "빌드+배포"이고 "소스 복사"는 사람이 한다.
2. **선택(권한 확보 후): `docs-sync-workflow.yml` 초안.** 비공개 저장소의 `.github/workflows/docs-sync.yml`에 두고 `docs/site/`를 `rsync -a --delete`로 공개 저장소에 반영한다. `.git`·`.github`·`site/`는 제외하고, 첫 실행은 `dry_run: true`(기본값)로 차이만 확인한다. 필요한 것: 비공개 저장소 Actions 사용 가능, 공개 저장소 `Contents: write` 토큰(`DOCS_SYNC_TOKEN`).
3. 공개 저장소가 비공개 저장소를 직접 당겨오는 방식은 쓰지 않는다(교차 저장소 읽기에 결국 같은 토큰이 필요하고, 공개 저장소에 제품 접근 권한이 생긴다).

### 2.3 DocFX API: CI에서 생성하지 않고 커밋된 `api-metadata`를 쓴다

- `scripts/generate_api.py`는 제품 소스(`Runtime/Core`, `Runtime/Unity`, `Editor`)와 로컬 Unity 6000.4.1f1 참조 어셈블리, 로컬 `docfx`가 필요하다. 공개 저장소·CI에는 셋 다 없다(제품 소스·어셈블리를 공개하지 않는다는 방침과 충돌).
- CI는 커밋된 `api-metadata/**/*.yml`을 **읽기만** 하고 `docfx build docfx/docfx.json --warningsAsErrors`로 HTML을 만든다. `docfx.json`도 `disableGitFeatures: true`라 저장소 이력이 필요 없다(`fetch-depth: 1`로 충분).
- API 갱신은 릴리스 준비 때 lead가 로컬에서 `generate_api.py`를 돌려 메타데이터를 커밋하는 현재 절차를 유지한다. `api-metadata/manifest.json`에 `docfx_version`, `unity_version`, `source_sha256`이 남으므로 어느 제품 리비전에서 만든 참조인지 추적할 수 있다.
- 주의: 메타데이터가 낡아도 CI는 성공한다(문서와 API의 불일치는 자동으로 잡히지 않는다). 릴리스 체크리스트에서 `manifest.json`의 `source_sha256`과 제품 커밋을 대조하는 항목을 두는 편이 낫다.

### 2.4 빌드 엄격도

`scripts/build.py`가 이미 다음을 한 번에 수행하므로 CI는 이 명령 하나만 호출한다.

- `mkdocs build --strict` (경고 = 실패)
- `docfx build --warningsAsErrors --disableGitFeatures`
- `scripts/check_content.py` (영문 전용, 로컬 경로 금지, HTML 링크·앵커 검사)

워크플로에는 도구 버전 고정(`docfx 2.81.0`, Python 3.12, `requirements.txt`)과 버전 출력 단계를 넣어 재현 가능하게 했다.

## 3. 활성화 전에 필요한 것 (lead/사용자)

1. 공개 저장소에 워크플로 파일을 push할 수 있는 토큰(`workflow` 스코프) 또는 GitHub 웹 UI로 `.github/workflows/pages.yml` 생성. 현재 토큰에는 이 권한이 없다.
2. 공개 저장소 Settings → Pages → Source를 "GitHub Actions"로 변경.
3. (선택) 2.2의 자동 동기화를 쓰려면 비공개 저장소 Actions 활성화 + `DOCS_SYNC_TOKEN` 시크릿.
4. 위 1~2가 끝나기 전에는 기존 수동 절차(`ghp-import -n -p site`)를 그대로 쓴다. 이 초안들은 어떤 것도 자동 실행되지 않는다.

## 4. 로컬 검증 (2026-11-21, release R1)

- 환경: Python 3.12.5, mkdocs 1.6.1, mkdocs-material 9.8.0, PyYAML 6.0.3, .NET 8.0.101, docfx 2.81.0.
- `python scripts/build.py --output .work/docs-site-build` → **성공, 종료 코드 0**. MkDocs 엄격 빌드 경고 0, DocFX `0 warning(s) / 0 error(s)`, `check_content.py` 통과(HTML 453개, 로컬 링크·앵커 유효, 영문·메타데이터 정리 확인).
- 산출물: HTML 453개, 합계 약 52MiB(이미지 포함). GitHub Pages 배포 한도(1GB) 안이다.
- 워크플로 초안은 YAML 파서로 문법만 확인했다. GitHub Actions에서 실제 실행해 본 적은 없다.
