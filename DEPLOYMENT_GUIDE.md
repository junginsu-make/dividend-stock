# Vercel 배포 가이드

## 📋 사전 요구사항
- GitHub 계정
- Vercel 계정 (GitHub으로 로그인 가능)

---

## 🚀 배포 단계

### 1. GitHub 저장소 생성 및 푸시

```bash
# 프로젝트 폴더에서 실행
git init
git add .
git commit -m "Initial commit: Dividend Optimizer"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/dividend-optimizer.git
git push -u origin main
```

### 2. Vercel 연결

1. [vercel.com](https://vercel.com) 접속 → **GitHub으로 로그인**
2. **Add New... → Project**
3. 방금 만든 저장소 선택
4. **Framework Preset**: `Other` 선택
5. **Root Directory**: `.` (기본값)
6. **Deploy** 클릭

### 3. 배포 확인

- 배포 완료 시 `https://your-project.vercel.app` URL 제공
- 해당 URL로 접속하여 사이트 확인

---

## ⏰ 자동 데이터 업데이트

GitHub Actions가 자동으로 하루 2회 데이터를 수집합니다:

| 시간 (KST) | 목적 |
|-----------|------|
| **06:30** | 미국 정규장 마감 후 (종가 반영) |
| **18:00** | 미국 프리마켓 시작 전 |

### GitHub Actions 활성화

1. GitHub 저장소 → **Actions** 탭
2. 워크플로우 활성화 확인
3. **수동 실행**: `Run workflow` 버튼으로 테스트 가능

---

## 📁 프로젝트 구조

```
dividend-optimizer/
├── .github/
│   └── workflows/
│       └── update-dividend-data.yml  # 자동 데이터 수집
├── api/
│   └── index.py                      # Vercel 서버리스 함수
├── templates/
│   ├── index.html
│   ├── dashboard.html
│   └── dividend.html
├── us_market/
│   └── dividend/
│       ├── config/
│       ├── data/
│       ├── engine.py
│       ├── loader.py
│       └── ...
├── vercel.json                        # Vercel 설정
└── requirements.txt                   # Python 의존성
```

---

## 🔧 문제 해결

### 배포 실패 시
1. Vercel 대시보드 → **Deployments** → 실패한 배포 클릭
2. **Build Logs** 확인
3. 일반적인 문제:
   - `requirements.txt` 의존성 오류 → 버전 확인
   - 경로 오류 → `api/index.py`의 경로 확인

### 데이터 업데이트 안 될 때
1. GitHub → **Actions** 탭 → 워크플로우 실행 기록 확인
2. `.github/workflows/update-dividend-data.yml` 파일 존재 확인
3. Repository Settings → Actions → General → **Allow all actions** 확인

---

## 📞 URL 엔드포인트

| 경로 | 설명 |
|------|------|
| `/` | 랜딩 페이지 |
| `/app` | 대시보드 |
| `/dividend` | 배당 최적화 |
| `/api/dividend/themes` | 테마 목록 API |
| `/api/dividend/all-tiers` | 포트폴리오 생성 API |
