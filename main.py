import sys, threading, time
from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QTextEdit
from sitemap_utils import collect_urls_from_sitemap
from typing import List
import pandas as pd
from tenacity import retry, wait_exponential, stop_after_attempt
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog,
                               QLabel, QComboBox, QTableWidget, QTableWidgetItem, QMessageBox)
from PySide6.QtCore import Qt, Signal, QObject

from gauth import get_credentials
from gsc_api import list_sites, inspect_url, site_matches_url, map_status, advice
from io_utils import load_urls_from_csv, normalize_url, export_results_csv

class WorkerSignals(QObject):
    progress = Signal(int, int)  # done, total
    row = Signal(dict)
    finished = Signal()

class InspectorWorker(threading.Thread):
    def __init__(self, creds, site_url: str, urls: List[str], signals: WorkerSignals, rpm: int = 300):
        super().__init__(daemon=True)
        self.creds = creds
        self.site_url = site_url
        self.urls = urls
        self.signals = signals
        self.interval = max(60.0 / max(1, rpm), 0.15)  # 粗略限速：每分钟请求数
        self._stop = False

    def stop(self):
        self._stop = True

    @retry(wait=wait_exponential(multiplier=1, min=1, max=32), stop=stop_after_attempt(5))
    def _inspect_once(self, u: str) -> dict:
        return inspect_url(self.creds, self.site_url, u)

    def run(self):
        total = len(self.urls)
        for i, u in enumerate(self.urls, 1):
            if self._stop: break
            try:
                data = self._inspect_once(u)
                row = {"url": u, **data}
                row["status"] = map_status(row)
                row["advice"] = advice(row)
                self.signals.row.emit(row)
            except Exception as e:
                self.signals.row.emit({"url": u, "error": str(e), "status": "error"})
            self.signals.progress.emit(i, total)
            time.sleep(self.interval)
        self.signals.finished.emit()

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Indexing Checker (GSC 精确模式)")
        self.resize(1000, 640)

        self.creds = None
        self.sites = []
        self.urls = []
        self.rows: list[dict] = []
        self.worker: InspectorWorker | None = None

        layout = QVBoxLayout(self)

        self.authBtn = QPushButton("① 登录 Google")
        self.authBtn.clicked.connect(self.on_login)
        layout.addWidget(self.authBtn)

        self.siteLabel = QLabel("② 选择 GSC 属性：")
        self.siteCombo = QComboBox()
        layout.addWidget(self.siteLabel)
        layout.addWidget(self.siteCombo)

        self.loadBtn = QPushButton("③ 导入 CSV（含 url/address 列）")
        self.loadBtn.clicked.connect(self.on_load_csv)
        layout.addWidget(self.loadBtn)
        
                # —— 新增：Sitemap 输入与按钮 ——
        sm_row = QHBoxLayout()
        self.sitemapInput = QLineEdit()
        self.sitemapInput.setPlaceholderText("在此输入 Sitemap URL（支持 .xml / .gz / 索引）")
        self.sitemapBtn = QPushButton("从 Sitemap 读取")
        self.sitemapBtn.clicked.connect(self.on_load_sitemap)
        sm_row.addWidget(self.sitemapInput)
        sm_row.addWidget(self.sitemapBtn)
        layout.addLayout(sm_row)

        # —— 新增：手动多行 URL 粘贴区 ——
        self.manualText = QTextEdit()
        self.manualText.setPlaceholderText("在此粘贴多条 URL，每行一条；点击右侧按钮加入待检")
        self.manualText.setFixedHeight(100)
        manual_row = QHBoxLayout()
        manual_row.addWidget(self.manualText)
        self.addManualBtn = QPushButton("添加手动 URL")
        self.addManualBtn.clicked.connect(self.on_add_manual_urls)
        manual_row.addWidget(self.addManualBtn)
        layout.addLayout(manual_row)


        self.startBtn = QPushButton("④ 开始检查")
        self.startBtn.clicked.connect(self.on_start)
        layout.addWidget(self.startBtn)

        self.progressLabel = QLabel("进度：0/0")
        layout.addWidget(self.progressLabel)

        self.table = QTableWidget(0, 9)
        self.table.setHorizontalHeaderLabels(["url","status","coverageState","verdict","pageFetchState","robotsTxtState","indexingState","lastCrawlTime","advice"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        self.exportBtn = QPushButton("导出结果 CSV")
        self.exportBtn.clicked.connect(self.on_export)
        layout.addWidget(self.exportBtn)

    def on_login(self):
        try:
            self.creds = get_credentials()
            self.sites = list_sites(self.creds)
            self.siteCombo.clear()
            self.siteCombo.addItems(self.sites)
            QMessageBox.information(self, "成功", f"登录成功，检测到 {len(self.sites)} 个属性。")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"登录失败：{e}")

    def _merge_urls(self, new_urls: list[str]):
        # 统一规范化、去重
        from io_utils import normalize_url
        existing = set(self.urls)
        added = 0
        for u in new_urls:
            u = u.strip()
            if not u: continue
            nu = normalize_url(u)
            if nu not in existing:
                existing.add(nu); added += 1
        self.urls = sorted(existing)
        QMessageBox.information(self, "加入完成", f"本次新增 {added} 条，当前待检共 {len(self.urls)} 条。")

    def on_load_sitemap(self):
        u = self.sitemapInput.text().strip()
        if not u:
            QMessageBox.information(self, "提示", "请先输入 Sitemap 地址。")
            return
        try:
            self.setEnabled(False)
            QApplication.setOverrideCursor(Qt.WaitCursor)
            urls = collect_urls_from_sitemap(u, max_depth=3, same_host_only=True)
            if not urls:
                QMessageBox.information(self, "结果", "未在该 Sitemap 中发现 URL。")
                return
            self._merge_urls(urls)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"Sitemap 读取失败：{e}")
        finally:
            QApplication.restoreOverrideCursor()
            self.setEnabled(True)

    def on_add_manual_urls(self):
        text = self.manualText.toPlainText()
        if not text.strip():
            QMessageBox.information(self, "提示", "请输入至少一条 URL。")
            return
        lines = [x.strip() for x in text.replace("\r\n","\n").split("\n")]
        lines = [x for x in lines if x]
        if not lines:
            QMessageBox.information(self, "提示", "未解析到有效 URL。")
            return
        self._merge_urls(lines)


    def on_load_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择 CSV 文件", "", "CSV Files (*.csv)")
        if not path: return
        try:
            self.urls = [normalize_url(u) for u in load_urls_from_csv(path)]
            QMessageBox.information(self, "已加载", f"共 {len(self.urls)} 条 URL。")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"读取失败：{e}")

    def on_start(self):
        if not self.creds:
            QMessageBox.warning(self, "提示", "请先登录 Google。")
            return
        if not self.urls:
            QMessageBox.warning(self, "提示", "请先导入 URL。")
            return
        site_url = self.siteCombo.currentText()
        # 过滤仅属于该属性的 URL（避免 API 报错）
        
                # 额外提示：当前待检数量
        if QMessageBox.question(self, "确认",
            f"将对 {len(self.urls)} 条 URL 发起检查（会做配额限速）。继续？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes) != QMessageBox.Yes:
            return

        
        targets = [u for u in self.urls if site_matches_url(site_url, u)]
        if not targets:
            QMessageBox.warning(self, "提示", "导入的 URL 不属于所选属性。")
            return

        self.rows.clear()
        self.table.setRowCount(0)

        self.signals = WorkerSignals()
        self.signals.progress.connect(self.on_progress)
        self.signals.row.connect(self.on_row)
        self.signals.finished.connect(self.on_finished)

        # 默认 300 RPM，可按需调小
        self.worker = InspectorWorker(self.creds, site_url, targets, self.signals, rpm=250)
        self.worker.start()
        self.startBtn.setEnabled(False)

    def on_progress(self, done, total):
        self.progressLabel.setText(f"进度：{done}/{total}")

    def on_row(self, row: dict):
        self.rows.append(row)
        self._append_table_row(row)

    def _append_table_row(self, r: dict):
        row_idx = self.table.rowCount()
        self.table.insertRow(row_idx)
        cols = ["url","status","coverageState","verdict","pageFetchState","robotsTxtState","indexingState","lastCrawlTime","advice"]
        for c, key in enumerate(cols):
            val = r.get(key, "")
            item = QTableWidgetItem(str(val))
            if key == "status":
                # 简单上色
                st = str(val)
                if st == "indexed": item.setBackground(Qt.green)
                elif st == "not_indexed": item.setBackground(Qt.yellow)
                elif st == "error": item.setBackground(Qt.red)
            self.table.setItem(row_idx, c, item)

    def on_finished(self):
        self.startBtn.setEnabled(True)
        QMessageBox.information(self, "完成", f"检查完成，共 {len(self.rows)} 条。")

    def on_export(self):
        if not self.rows:
            QMessageBox.information(self, "提示", "暂无结果可导出。")
            return
        path, _ = QFileDialog.getSaveFileName(self, "导出 CSV", "indexing_results.csv", "CSV Files (*.csv)")
        if not path: return
        df = pd.DataFrame(self.rows)
        export_results_csv(df, path)
        QMessageBox.information(self, "已导出", f"已导出到：{path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = App()
    w.show()
    sys.exit(app.exec())
