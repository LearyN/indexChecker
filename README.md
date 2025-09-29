# Indexing Checker (GSC 精确模式批量查询工具)

> 🇨🇳 一款基于 **Google Search Console API** 的桌面工具，用于批量检查 URL 收录状态。  
> 🇺🇸 A desktop tool based on **Google Search Console API** to batch check URL indexing status.

---

## 🔑 配置 Google OAuth 密钥 / Configure Google OAuth Credentials

在运行工具前，你需要在 Google Cloud Console 中启用 API 并创建 OAuth 密钥。  
Before running the tool, you must enable APIs in Google Cloud Console and create an OAuth client key.

### 1. 打开 Google Cloud Console  
- 🇨🇳 前往 [Google Cloud Console](https://console.cloud.google.com/)  
- 🇺🇸 Go to [Google Cloud Console](https://console.cloud.google.com/)

### 2. 创建项目 Create a Project  
- 🇨🇳 在左上角 **项目选择器** 中，新建一个项目（例如 `IndexChecker`）  
- 🇺🇸 In the top-left **Project Selector**, create a new project (e.g. `IndexChecker`)

### 3. 启用 API Enable APIs  
- 🇨🇳 在导航菜单中进入 **API 和服务 → 库**，搜索并启用：  
  - **Google Search Console API**  
- 🇺🇸 Go to **APIs & Services → Library**, search and enable:  
  - **Google Search Console API**

### 4. 配置 OAuth 同意屏幕 Configure OAuth Consent Screen  
- 🇨🇳 在 **API 和服务 → OAuth 同意屏幕** 中：  
  - 用户类型选择 **External 外部**  
  - 添加你的 Gmail 账号到 **测试用户**  
- 🇺🇸 In **APIs & Services → OAuth consent screen**:  
  - Select **External** as user type  
  - Add your Gmail account under **Test users**

### 5. 创建 OAuth 客户端 ID Create OAuth Client ID  
- 🇨🇳 在 **API 和服务 → 凭据 (Credentials)** 中：  
  - 点击 **创建凭据 → OAuth 客户端 ID**  
  - 应用类型选择 **桌面应用 (Desktop App)**  
  - 下载生成的 JSON 文件，重命名为 **`client_secret.json`**  
- 🇺🇸 In **APIs & Services → Credentials**:  
  - Click **Create Credentials → OAuth client ID**  
  - Select **Desktop App** as application type  
  - Download the generated JSON file and rename it to **`client_secret.json`**

### 6. 放置密钥文件 Place the Key File  
- 🇨🇳 将 `client_secret.json` 放到与 `IndexingChecker.exe` 相同的目录  
- 🇺🇸 Put `client_secret.json` in the same directory as `IndexingChecker.exe`

完成以上步骤后，你就可以正常登录 Google 并使用本工具了 ✅  
After completing these steps, you can log in with Google and use the tool ✅

## 🚀 使用教程 (EXE 版 Usage Guide for EXE)

### 1. 下载与准备 Download & Setup
- 🇨🇳 打开仓库的 [dist 目录](https://github.com/LearyN/indexChecker/tree/main/dist)，下载最新的 **IndexingChecker.exe**  
- 🇺🇸 Open the [dist folder](https://github.com/LearyN/indexChecker/tree/main/dist) in this repo and download the latest **IndexingChecker.exe**

- 🇨🇳 从 [Google Cloud Console](https://console.cloud.google.com/) 下载 OAuth 客户端密钥，命名为 **`client_secret.json`**  
- 🇺🇸 Download your OAuth client credentials from [Google Cloud Console](https://console.cloud.google.com/) and rename it to **`client_secret.json`**

- 🇨🇳 将 `client_secret.json` 放到与 `IndexingChecker.exe` 相同的目录  
- 🇺🇸 Place `client_secret.json` in the same folder as `IndexingChecker.exe`

---

### 2. 首次运行 First Run
- 🇨🇳 双击 `IndexingChecker.exe` → 点击 **登录 Google**  
- 🇺🇸 Double-click `IndexingChecker.exe` → Click **Login Google**

- 🇨🇳 浏览器会打开授权页面，使用有 GSC 权限的 Gmail 登录并允许 API 访问  
- 🇺🇸 A browser window will open, log in with your Gmail that has GSC access and allow permissions

- 🇨🇳 授权完成后，目录下会生成 **`token.json`**，下次运行可直接使用  
- 🇺🇸 After authorization, a **`token.json`** will be created; future runs will reuse it automatically

---

### 3. 导入 URL 的三种方式 Three Ways to Import URLs

#### 📂 导入 CSV Import CSV
- 🇨🇳 准备一个包含 `url` 或 `address` 列的 CSV 文件 → 点击「导入 CSV」  
- 🇺🇸 Prepare a CSV file with a `url` or `address` column → Click "Import CSV"

#### 🌐 输入 Sitemap Enter Sitemap
- 🇨🇳 在输入框填入 `https://example.com/sitemap.xml`（支持 `.xml` / `.gz` / 索引）→ 点击「从 Sitemap 读取」  
- 🇺🇸 Enter `https://example.com/sitemap.xml` (supports `.xml` / `.gz` / index files) → Click "Load from Sitemap"

#### ✍️ 手动输入 URL Manual Input
- 🇨🇳 在多行框中粘贴 URL（每行一条）→ 点击「添加手动 URL」  
- 🇺🇸 Paste URLs in the multi-line text box (one per line) → Click "Add Manual URL"

---

### 4. 开始检查 Start Inspection
- 🇨🇳 点击「开始检查」，工具会逐一调用 GSC API  
- 🇺🇸 Click "Start Inspection", the tool will query each URL via GSC API

- 🇨🇳 结果显示在表格中，包括：  
  - 收录状态 `status`  
  - 覆盖情况 `coverageState`  
  - 抓取情况 `pageFetchState`  
  - Robots 规则 `robotsTxtState`  
  - 最近抓取时间 `lastCrawlTime`  
  - 优化建议 `advice`  
- 🇺🇸 Results are shown in the table, including:  
  - Indexing status `status`  
  - Coverage `coverageState`  
  - Fetch status `pageFetchState`  
  - Robots rule `robotsTxtState`  
  - Last crawl time `lastCrawlTime`  
  - SEO advice `advice`

---

### 5. 导出结果 Export Results
- 🇨🇳 点击「导出结果 CSV」即可保存查询结果  
- 🇺🇸 Click "Export Results CSV" to save results for analysis

---

## ⚠️ 注意事项 Notes
- 🇨🇳 目录中必须有 `client_secret.json`，否则无法登录  
- 🇺🇸 `client_secret.json` must exist in the same folder, otherwise login will fail  

- 🇨🇳 `token.json` 会在首次授权后生成，请勿删除  
- 🇺🇸 `token.json` is generated after first login, do not delete  

- 🇨🇳 Google Search Console API 有调用配额，建议分批导入 URL  
- 🇺🇸 GSC API has quota limits, split large URL lists into batches  

- 🇨🇳 请勿上传 `client_secret.json` 和 `token.json` 到 GitHub 或公开分享  
- 🇺🇸 Do not upload `client_secret.json` or `token.json` to GitHub or share publicly  

---

## 🖥️ 适用场景 Use Cases
- 🇨🇳 批量检查 sitemap 中 URL 的收录情况  
- 🇨🇳 对比不同页面的 GSC 索引状态  
- 🇨🇳 SEO 日常监控与收录问题排查  
- 🇺🇸 Batch check sitemap URLs indexing status  
- 🇺🇸 Compare indexing states of multiple pages in GSC  
- 🇺🇸 Daily SEO monitoring and troubleshooting

---

