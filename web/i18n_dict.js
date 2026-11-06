/* 介面翻譯對照表：中文 → [English, Bahasa Indonesia]。由 tools/dev/i18n_build.py 產生，用法見 i18n.js。 */
window.I18N_DICT = {
"   召回率={0}": [
"   Recall={0}",
"   Recall={0}"
],
"  區網：http://{0}:{1}/": [
"  LAN: http://{0}:{1}/",
"  LAN: http://{0}:{1}/"
],
"  本機：http://127.0.0.1:{0}/   監控頁；標記頁 http://127.0.0.1:{1}/label": [
"  This PC: http://127.0.0.1:{0}/   Monitor page; label page http://127.0.0.1:{1}/label",
"  PC ini: http://127.0.0.1:{0}/   Halaman pantau; halaman tandai http://127.0.0.1:{1}/label"
],
" {0} 秒": [
" {0} s",
" {0} detik"
],
" 候選 {0}": [
" Candidate {0}",
" Kandidat {0}"
],
" 缺：{0}": [
" Missing: {0}",
" Kurang: {0}"
],
"0 秒＝警告多久就叫多久。主機蜂鳴器裝在跑監控的那台電腦上，不管有沒有人開著這個網頁都會響。試跑不響。": [
"0 s = sound for as long as the alert lasts. The host buzzer is on the PC running the monitor and sounds whether or not anyone has this page open. Silent during trial runs.",
"0 dtk = berbunyi selama peringatan masih ada. Buzzer host ada di PC yang menjalankan pemantauan dan tetap berbunyi walau halaman ini tidak dibuka. Tidak berbunyi saat uji coba."
],
"1. 解壓縮：unzip <這個檔> -d sopg_train && cd sopg_train\\n": [
"1. Unzip: unzip <this file> -d sopg_train && cd sopg_train\\n",
"1. Ekstrak: unzip <file ini> -d sopg_train && cd sopg_train\\n"
],
"2. 用已經裝好 ultralytics 的 Python 跑（GPU 會自動用）：\\n": [
"2. Run with a Python that has ultralytics installed (GPU is used automatically):\\n",
"2. Jalankan dengan Python yang sudah ada ultralytics (GPU dipakai otomatis):\\n"
],
"3. 跑完把 out/best.pt 拷回這台電腦，在「包裝方式設定 → 訓練辨識模型」按「匯入 GPU 訓練好的模型」，\\n": [
"3. When done, copy out/best.pt back to this computer, go to \"Packing method settings → Train detection model\" and click \"Import GPU-trained model\",\\n",
"3. Setelah selesai, salin out/best.pt ke komputer ini, buka \"Pengaturan metode kemas → Latih model deteksi\" lalu klik \"Impor model hasil latih GPU\",\\n"
],
"3. 跑完把 out/best.pt 拷回這台電腦，在「包裝明細 → 訓練辨識模型」按「匯入 GPU 訓練好的模型」，\\n": [
"3. When done, copy out/best.pt back to this computer, go to \"Packing details → Train detection model\" and click \"Import GPU-trained model\",\\n",
"3. Setelah selesai, salin out/best.pt ke komputer ini, buka \"Rincian kemas → Latih model deteksi\" lalu klik \"Impor model hasil latih GPU\",\\n"
],
"</div><div class=\"da\"><button class=\"btn btn-cancel\" id=\"shClose\">關閉</button><span></span></div></div>": [
"</div><div class=\"da\"><button class=\"btn btn-cancel\" id=\"shClose\">Close</button><span></span></div></div>",
"</div><div class=\"da\"><button class=\"btn btn-cancel\" id=\"shClose\">Tutup</button><span></span></div></div>"
],
"<button class=\"btn btn-secondary raised\" id=\"shSaveRoot\" style=\"height:30px\">儲存並讀取</button>": [
"<button class=\"btn btn-secondary raised\" id=\"shSaveRoot\" style=\"height:30px\">Save and load</button>",
"<button class=\"btn btn-secondary raised\" id=\"shSaveRoot\" style=\"height:30px\">Simpan dan muat</button>"
],
"<details><summary style=\"cursor:pointer;color:var(--primary);font-size:13px\">怎麼判好壞</summary><div class=\"hint2\" id=\"trRule\" style=\"line-height:1.7;padding-top:4px\"></div></details>": [
"<details><summary style=\"cursor:pointer;color:var(--primary);font-size:13px\">How better/worse is judged</summary><div class=\"hint2\" id=\"trRule\" style=\"line-height:1.7;padding-top:4px\"></div></details>",
"<details><summary style=\"cursor:pointer;color:var(--primary);font-size:13px\">Cara menilai baik/buruk</summary><div class=\"hint2\" id=\"trRule\" style=\"line-height:1.7;padding-top:4px\"></div></details>"
],
"<details><summary style=\"cursor:pointer;color:var(--primary);font-size:13px\">最近幾次訓練</summary><div style=\"overflow-x:auto;padding-top:4px\"><table class=\"grid n\" id=\"trHist\"></table></div></details>": [
"<details><summary style=\"cursor:pointer;color:var(--primary);font-size:13px\">Recent trainings</summary><div style=\"overflow-x:auto;padding-top:4px\"><table class=\"grid n\" id=\"trHist\"></table></div></details>",
"<details><summary style=\"cursor:pointer;color:var(--primary);font-size:13px\">Latihan terakhir</summary><div style=\"overflow-x:auto;padding-top:4px\"><table class=\"grid n\" id=\"trHist\"></table></div></details>"
],
"<div class=\"dialog\" role=\"dialog\" aria-modal=\"true\" aria-labelledby=\"pcTitle\" style=\"width:min(640px,calc(100vw - 32px));height:auto\">\n      <div class=\"dt\"><span class=\"mi mark\">settings</span><h4 id=\"pcTitle\">這台電腦的產線</h4></div>\n      <div class=\"dc\">\n        <div class=\"row2\">\n          <div class=\"fld w140\"><label for=\"pcName\">產線名稱 *</label><input id=\"pcName\" placeholder=\"例如 包裝 1 線\"></div>\n          <div class=\"fld w100\"><label for=\"pcFactory\">廠別</label><select id=\"pcFactory\"><option value=\"\">（不接）</option><option>BYI</option><option>GGV</option></select></div>\n          <div class=\"fld w140\"><label>站別（電腦名稱，自動帶）</label><div class=\"ro n\" id=\"pcStation\"></div></div>\n        </div>\n        <div class=\"fld\" style=\"width:100%\"><label for=\"pcCamera\">相機（編號 0、1… 或 rtsp 網址；密碼只存在這台電腦、畫面上遮成 ***）</label><input id=\"pcCamera\" placeholder=\"rtsp://帳號:密碼@相機位址:554/stream1\"></div>\n        <div class=\"row2\">\n          <div class=\"fld w100\"><label for=\"pcType\">製程類別</label><select id=\"pcType\"><option value=\"140\">組底</option><option value=\"150\">裁斷</option><option value=\"160\">針車</option><option value=\"170\">成型</option></select></div>\n          <div class=\"fld w200\"><label for=\"pcEip\">EIP 產線（不選＝不上傳統計）</label><select id=\"pcEip\"><option value=\"\">（不接）</option></select></div>\n          <div class=\"fld w120\"><label for=\"pcLabel\">站別顯示名稱</label><input id=\"pcLabel\" placeholder=\"例如 A 站\"></div>\n        </div>\n        <div class=\"hint2\" id=\"pcMsg\" style=\"font-size:12.5px;color:var(--ink-2)\"></div>\n        <div class=\"note danger\" id=\"pcErr\" hidden></div>\n      </div>\n      <div class=\"da\"><button class=\"btn btn-cancel\" id=\"pcCancel\">取消</button><button class=\"btn btn-primary raised\" id=\"pcSave\">儲存</button></div>\n    </div>": [
"\n    <div class=\"dialog\" role=\"dialog\" aria-modal=\"true\" aria-labelledby=\"pcTitle\" style=\"width:min(640px,calc(100vw - 32px));height:auto\">\n      <div class=\"dt\"><span class=\"mi mark\">settings</span><h4 id=\"pcTitle\">Line for this computer</h4></div>\n      <div class=\"dc\">\n        <div class=\"row2\">\n          <div class=\"fld w140\"><label for=\"pcName\">Line name *</label><input id=\"pcName\" placeholder=\"e.g. Packing line 1\"></div>\n          <div class=\"fld w100\"><label for=\"pcFactory\">Factory</label><select id=\"pcFactory\"><option value=\"\">(not linked)</option><option>BYI</option><option>GGV</option></select></div>\n          <div class=\"fld w140\"><label>Station (computer name, auto-filled)</label><div class=\"ro n\" id=\"pcStation\"></div></div>\n        </div>\n        <div class=\"fld\" style=\"width:100%\"><label for=\"pcCamera\">Camera (number 0, 1… or rtsp URL; password is stored only on this computer and shown as ***)</label><input id=\"pcCamera\" placeholder=\"rtsp://user:password@camera-address:554/stream1\"></div>\n        <div class=\"row2\">\n          <div class=\"fld w100\"><label for=\"pcType\">Process type</label><select id=\"pcType\"><option value=\"140\">Stock fitting</option><option value=\"150\">Cutting</option><option value=\"160\">Sewing</option><option value=\"170\">Assembly</option></select></div>\n          <div class=\"fld w200\"><label for=\"pcEip\">EIP line (none = no stats upload)</label><select id=\"pcEip\"><option value=\"\">(not linked)</option></select></div>\n          <div class=\"fld w120\"><label for=\"pcLabel\">Station display name</label><input id=\"pcLabel\" placeholder=\"e.g. Station A\"></div>\n        </div>\n        <div class=\"hint2\" id=\"pcMsg\" style=\"font-size:12.5px;color:var(--ink-2)\"></div>\n        <div class=\"note danger\" id=\"pcErr\" hidden></div>\n      </div>\n      <div class=\"da\"><button class=\"btn btn-cancel\" id=\"pcCancel\">Cancel</button><button class=\"btn btn-primary raised\" id=\"pcSave\">Save</button></div>\n    </div>",
"\n    <div class=\"dialog\" role=\"dialog\" aria-modal=\"true\" aria-labelledby=\"pcTitle\" style=\"width:min(640px,calc(100vw - 32px));height:auto\">\n      <div class=\"dt\"><span class=\"mi mark\">settings</span><h4 id=\"pcTitle\">Lini komputer ini</h4></div>\n      <div class=\"dc\">\n        <div class=\"row2\">\n          <div class=\"fld w140\"><label for=\"pcName\">Nama lini *</label><input id=\"pcName\" placeholder=\"misal Lini kemas 1\"></div>\n          <div class=\"fld w100\"><label for=\"pcFactory\">Pabrik</label><select id=\"pcFactory\"><option value=\"\">(tidak disambung)</option><option>BYI</option><option>GGV</option></select></div>\n          <div class=\"fld w140\"><label>Stasiun (nama komputer, otomatis)</label><div class=\"ro n\" id=\"pcStation\"></div></div>\n        </div>\n        <div class=\"fld\" style=\"width:100%\"><label for=\"pcCamera\">Kamera (nomor 0, 1… atau URL rtsp; kata sandi hanya disimpan di komputer ini dan tampil sebagai ***)</label><input id=\"pcCamera\" placeholder=\"rtsp://user:sandi@alamat-kamera:554/stream1\"></div>\n        <div class=\"row2\">\n          <div class=\"fld w100\"><label for=\"pcType\">Jenis proses</label><select id=\"pcType\"><option value=\"140\">Stock fitting</option><option value=\"150\">Cutting</option><option value=\"160\">Jahit</option><option value=\"170\">Assembly</option></select></div>\n          <div class=\"fld w200\"><label for=\"pcEip\">Lini EIP (kosong = statistik tidak diunggah)</label><select id=\"pcEip\"><option value=\"\">(tidak disambung)</option></select></div>\n          <div class=\"fld w120\"><label for=\"pcLabel\">Nama tampilan stasiun</label><input id=\"pcLabel\" placeholder=\"misal Stasiun A\"></div>\n        </div>\n        <div class=\"hint2\" id=\"pcMsg\" style=\"font-size:12.5px;color:var(--ink-2)\"></div>\n        <div class=\"note danger\" id=\"pcErr\" hidden></div>\n      </div>\n      <div class=\"da\"><button class=\"btn btn-cancel\" id=\"pcCancel\">Batal</button><button class=\"btn btn-primary raised\" id=\"pcSave\">Simpan</button></div>\n    </div>"
],
"<div class=\"dt\"><span class=\"mi mark\">cloud</span><h4 id=\"shTitle\">共用硬碟</h4><span class=\"sum n\" id=\"shSum\"></span></div>": [
"<div class=\"dt\"><span class=\"mi mark\">cloud</span><h4 id=\"shTitle\">Shared drive</h4><span class=\"sum n\" id=\"shSum\"></span></div>",
"<div class=\"dt\"><span class=\"mi mark\">cloud</span><h4 id=\"shTitle\">Drive bersama</h4><span class=\"sum n\" id=\"shSum\"></span></div>"
],
"<div class=\"frow\" style=\"align-items:flex-end\"><div class=\"fld w320\"><label for=\"shRoot\">共用硬碟資料夾（這台電腦記住，之後不用再填）</label><input id=\"shRoot\" placeholder=\"例如 \\\\\\\\NAS01\\\\SOP-Guard\\\\projects\"></div>": [
"<div class=\"frow\" style=\"align-items:flex-end\"><div class=\"fld w320\"><label for=\"shRoot\">Shared drive folder (remembered on this computer, no need to enter again)</label><input id=\"shRoot\" placeholder=\"e.g. \\\\\\\\NAS01\\\\SOP-Guard\\\\projects\"></div>",
"<div class=\"frow\" style=\"align-items:flex-end\"><div class=\"fld w320\"><label for=\"shRoot\">Folder drive bersama (diingat di komputer ini, tidak perlu isi lagi)</label><input id=\"shRoot\" placeholder=\"misal \\\\\\\\NAS01\\\\SOP-Guard\\\\projects\"></div>"
],
"<div class=\"note info\">上傳＝在共用硬碟新增一版（舊版都留著，不會被蓋掉），並設成目前版本。別人在你載入之後又傳過時，會先問要不要設成目前版本。沒有模型的專案也能上傳，讓別台電腦拿去訓練。</div></div>": [
"<div class=\"note info\">Upload = add a new version on the shared drive (old versions are kept, never overwritten) and set it as current. If someone else uploaded after you loaded, you will be asked first whether to set it as current. Projects without a model can also be uploaded so another computer can train them.</div></div>",
"<div class=\"note info\">Unggah = tambah versi baru di drive bersama (versi lama tetap ada, tidak ditimpa) dan jadikan versi aktif. Jika orang lain mengunggah setelah Anda memuat, akan ditanya dulu apakah mau dijadikan versi aktif. Proyek tanpa model juga bisa diunggah supaya komputer lain bisa melatihnya.</div></div>"
],
"<div class=\"note info\">載入＝把共用硬碟上那一版的設定、步驟、框、辨識模型複製到這台電腦，不用重訓。載入後到監控畫面「操作 → 換包裝方式」就能選。共用硬碟的檔案不會被改。</div></div>": [
"<div class=\"note info\">Load = copy that version's settings, steps, boxes and recognition model from the shared drive to this computer, no retraining needed. After loading, select it in Monitor screen \"Actions → Change packing method\". Files on the shared drive are not changed.</div></div>",
"<div class=\"note info\">Muat = salin pengaturan, langkah, kotak, dan model pengenal versi itu dari drive bersama ke komputer ini, tidak perlu latih ulang. Setelah dimuat, pilih di Layar pantau \"Aksi → Ganti metode kemas\". File di drive bersama tidak diubah.</div></div>"
],
"<div class=\"note warn\" id=\"shConfirm\" hidden style=\"align-items:center;gap:10px\"><span id=\"shConfirmText\" style=\"flex:1\"></span><button class=\"btn btn-primary raised\" id=\"shConfirmOk\" style=\"height:28px\">設成目前版本</button><button class=\"btn btn-cancel\" id=\"shConfirmNo\" style=\"height:28px\">先不要</button></div>": [
"<div class=\"note warn\" id=\"shConfirm\" hidden style=\"align-items:center;gap:10px\"><span id=\"shConfirmText\" style=\"flex:1\"></span><button class=\"btn btn-primary raised\" id=\"shConfirmOk\" style=\"height:28px\">Set as current version</button><button class=\"btn btn-cancel\" id=\"shConfirmNo\" style=\"height:28px\">Not now</button></div>",
"<div class=\"note warn\" id=\"shConfirm\" hidden style=\"align-items:center;gap:10px\"><span id=\"shConfirmText\" style=\"flex:1\"></span><button class=\"btn btn-primary raised\" id=\"shConfirmOk\" style=\"height:28px\">Jadikan versi aktif</button><button class=\"btn btn-cancel\" id=\"shConfirmNo\" style=\"height:28px\">Nanti dulu</button></div>"
],
"<div class=\"tabs\" role=\"tablist\" id=\"shTabs\"><button data-stab=\"load\" class=\"on\">載入到這台電腦</button><button data-stab=\"up\">上傳這台電腦的專案</button></div>": [
"<div class=\"tabs\" role=\"tablist\" id=\"shTabs\"><button data-stab=\"load\" class=\"on\">Load to this computer</button><button data-stab=\"up\">Upload this computer's projects</button></div>",
"<div class=\"tabs\" role=\"tablist\" id=\"shTabs\"><button data-stab=\"load\" class=\"on\">Muat ke komputer ini</button><button data-stab=\"up\">Unggah proyek komputer ini</button></div>"
],
"<div id=\"shPaneUp\" hidden><div class=\"frow\"><div class=\"fld\" style=\"width:100%\"><label for=\"shNote\">這版改了什麼（選填，寫進版本紀錄）</label><input id=\"shNote\" placeholder=\"例如 加了白鞋的框\"></div></div>": [
"<div id=\"shPaneUp\" hidden><div class=\"frow\"><div class=\"fld\" style=\"width:100%\"><label for=\"shNote\">What changed in this version (optional, saved in version history)</label><input id=\"shNote\" placeholder=\"e.g. added boxes for white shoes\"></div></div>",
"<div id=\"shPaneUp\" hidden><div class=\"frow\"><div class=\"fld\" style=\"width:100%\"><label for=\"shNote\">Apa yang diubah di versi ini (opsional, dicatat di riwayat versi)</label><input id=\"shNote\" placeholder=\"misal tambah kotak sepatu putih\"></div></div>"
],
"<label style=\"display:inline-flex;gap:6px;align-items:center;padding-bottom:6px\"><input type=\"checkbox\" id=\"shVideo\"> 連示範影片一起（要在別台補框或訓練才需要）</label></div>": [
"<label style=\"display:inline-flex;gap:6px;align-items:center;padding-bottom:6px\"><input type=\"checkbox\" id=\"shVideo\"> Include demo video (only needed to add boxes or train on another computer)</label></div>",
"<label style=\"display:inline-flex;gap:6px;align-items:center;padding-bottom:6px\"><input type=\"checkbox\" id=\"shVideo\"> Sertakan video contoh (hanya perlu untuk tambah kotak atau latih di komputer lain)</label></div>"
],
"<option value=''>（選專案）</option>": [
"<option value=''>(Select project)</option>",
"<option value=''>(Pilih proyek)</option>"
],
"<span class=\"mi ico\">settings</span><span class=\"txt\">這台電腦的產線</span>": [
"<span class=\"mi ico\">settings</span><span class=\"txt\">Line for this computer</span>",
"<span class=\"mi ico\">settings</span><span class=\"txt\">Lini komputer ini</span>"
],
"A. 用相機錄一段": [
"A. Record with the camera",
"A. Rekam dengan kamera"
],
"B. 上傳已經拍好的影片": [
"B. Upload a video you already shot",
"B. Unggah video yang sudah direkam"
],
"EIP 今日報工": [
"EIP today's report",
"Laporan EIP hari ini"
],
"EIP 已經 {0} 分鐘連不上：今天的型體清單和目標是舊的，監控照常；當天統計留在本機，連上後會補傳": [
"EIP offline for {0} min: today's style list and targets are old. Monitoring continues; today's stats stay on this PC and will be uploaded once reconnected",
"EIP tidak terhubung sudah {0} menit: daftar artikel dan target hari ini data lama. Pemantauan tetap jalan; statistik hari ini disimpan di PC ini dan dikirim setelah terhubung lagi"
],
"EIP 已連線": [
"EIP connected",
"EIP terhubung"
],
"EIP 產線": [
"EIP line",
"Lini EIP"
],
"EIP 產線（不選＝不上傳統計）": [
"EIP line (none = stats not uploaded)",
"Lini EIP (kosong = statistik tidak diunggah)"
],
"EIP 網址要以 http:// 或 https:// 開頭": [
"EIP URL must start with http:// or https://",
"URL EIP harus diawali http:// atau https://"
],
"EIP 轉數表今天這條線沒有訂單（沒建或沒填時段）": [
"No orders for this line today in the EIP rotation table (not created or no time slot filled)",
"Tidak ada order untuk lini ini hari ini di tabel rotasi EIP (belum dibuat atau slot waktu belum diisi)"
],
"EIP 連不上": [
"EIP offline",
"EIP tidak terhubung"
],
"EIP 連不上，這是": [
"EIP offline, this is ",
"EIP tidak terhubung, ini "
],
"EIP 還沒有上傳統計的 API（要 EIP 那邊開卡）": [
"EIP has no API for uploading stats yet (EIP team needs to open a ticket)",
"EIP belum punya API untuk upload statistik (tim EIP perlu buka tiket)"
],
"GPU 訓練包已產生（{0} MB）：{1}": [
"GPU training package created ({0} MB): {1}",
"Paket latih GPU sudah dibuat ({0} MB): {1}"
],
"Recorder 尚未 start": [
"Recorder not started yet",
"Recorder belum start"
],
"SOP-Guard GPU 訓練包\\n\\n": [
"SOP-Guard GPU training pack\\n\\n",
"Paket latih GPU SOP-Guard\\n\\n"
],
"SOP-Guard 包裝方式設定": [
"SOP-Guard Packing method settings",
"SOP-Guard Pengaturan metode kemas"
],
"SOP-Guard 包裝明細": [
"SOP-Guard Packing details",
"SOP-Guard Rincian kemas"
],
"SOP-Guard 包裝設定": [
"SOP-Guard Packing setup",
"SOP-Guard Pengaturan kemas"
],
"SOP-Guard 核心引擎開發測試入口": [
"SOP-Guard core engine dev test entry",
"Pintu uji pengembangan mesin inti SOP-Guard"
],
"SOP-Guard 標記物品": [
"SOP-Guard Label items",
"SOP-Guard Tandai barang"
],
"SOP-Guard 監控": [
"SOP-Guard Monitor",
"SOP-Guard Pantau"
],
"SOP-Guard 網頁版已啟動": [
"SOP-Guard web version started",
"SOP-Guard versi web sudah mulai"
],
"SOP-Guard 網頁版監控": [
"SOP-Guard Web Monitor",
"Pantau SOP-Guard Web"
],
"SOP-Guard 預覽（按 q 離開）": [
"SOP-Guard preview (press q to quit)",
"Pratinjau SOP-Guard (tekan q untuk keluar)"
],
"YOLO 用幾個 CPU 執行緒（留一些給 MediaPipe）": [
"Number of CPU threads for YOLO (leave some for MediaPipe)",
"Jumlah thread CPU untuk YOLO (sisakan untuk MediaPipe)"
],
"YOLO-World 權重（專案有 anchors 時需要）": [
"YOLO-World weights (needed when project has anchors)",
"Bobot YOLO-World (perlu jika proyek punya anchors)"
],
"[警告音] 此環境沒有 winsound，略過": [
"[Alert sound] winsound not available here, skipped",
"[Suara peringatan] winsound tidak tersedia di sini, dilewati"
],
"\\n失敗：": [
"\\nFailed: ",
"\\nGagal: "
],
"\\n把這個檔案複製到 GPU 電腦，解壓後照裡面的 README_GPU.txt 跑；訓練完把 out/best.pt 拷回來，按上面的「匯入並驗證」。": [
"\\nCopy this file to the GPU computer, unzip it and follow README_GPU.txt inside; after training, copy out/best.pt back and click \"Import and verify\" above.",
"\\nSalin file ini ke komputer GPU, ekstrak lalu ikuti README_GPU.txt di dalamnya; setelah selesai latih, salin out/best.pt kembali lalu klik \"Impor dan verifikasi\" di atas."
],
"anchors 名稱重複：{0}": [
"Duplicate anchors name: {0}",
"Nama anchors duplikat: {0}"
],
"anchors 必須是陣列": [
"anchors must be an array",
"anchors harus berupa array"
],
"anchors[{0}] 必須是物件": [
"anchors[{0}] must be an object",
"anchors[{0}] harus berupa objek"
],
"anchors[{0}].exclude_containing 必須是名稱陣列": [
"anchors[{0}].exclude_containing must be an array of names",
"anchors[{0}].exclude_containing harus berupa array nama"
],
"anchors[{0}].max_count 必須是 ≥1 的整數": [
"anchors[{0}].max_count must be an integer ≥1",
"anchors[{0}].max_count harus bilangan bulat ≥1"
],
"anchors[{0}].name 必須是非空字串": [
"anchors[{0}].name must be a non-empty string",
"anchors[{0}].name harus string yang tidak kosong"
],
"anchors[{0}].pick 只能是 {1}": [
"anchors[{0}].pick can only be {1}",
"anchors[{0}].pick hanya boleh {1}"
],
"anchors[{0}].prompt 必須是非空字串": [
"anchors[{0}].prompt must be a non-empty string",
"anchors[{0}].prompt harus string yang tidak kosong"
],
"anchors「{0}」.exclude_containing 的「{1}」不是其他錨點的名稱": [
"\"{1}\" in anchors \"{0}\".exclude_containing is not the name of another anchor",
"\"{1}\" di anchors \"{0}\".exclude_containing bukan nama anchor lain"
],
"config.json 不是合法的 JSON：{0}": [
"config.json is not valid JSON: {0}",
"config.json bukan JSON yang valid: {0}"
],
"config.json 最外層必須是物件": [
"config.json top level must be an object",
"Level teratas config.json harus berupa objek"
],
"cycle_arm_clear_sec 不可為負數": [
"cycle_arm_clear_sec cannot be negative",
"cycle_arm_clear_sec tidak boleh negatif"
],
"cycle_end 必須是物件或 null": [
"cycle_end must be an object or null",
"cycle_end harus berupa objek atau null"
],
"cycle_end.hold_sec 必須大於 0": [
"cycle_end.hold_sec must be greater than 0",
"cycle_end.hold_sec harus lebih dari 0"
],
"cycle_end.label（最後一步的名稱）必須是 null 或非空字串": [
"cycle_end.label (name of the last step) must be null or a non-empty string",
"cycle_end.label (nama langkah terakhir) harus null atau teks tidak kosong"
],
"cycle_end.type 只能是 {0}": [
"cycle_end.type can only be {0}",
"cycle_end.type hanya boleh {0}"
],
"cycle_min_sec 不可為負數": [
"cycle_min_sec cannot be negative",
"cycle_min_sec tidak boleh negatif"
],
"cycle_timeout_sec 必須是 null 或大於 0": [
"cycle_timeout_sec must be null or greater than 0",
"cycle_timeout_sec harus null atau lebih dari 0"
],
"detect_every_n_frames 必須是 ≥1 的整數": [
"detect_every_n_frames must be an integer ≥1",
"detect_every_n_frames harus bilangan bulat ≥1"
],
"fps 必須是大於 0 的數字": [
"fps must be a number greater than 0",
"fps harus angka lebih dari 0"
],
"gesture_anchors 必須是名稱陣列": [
"gesture_anchors must be an array of names",
"gesture_anchors harus berupa array nama"
],
"gesture_anchors「{0}」不存在於 anchors": [
"gesture_anchors \"{0}\" does not exist in anchors",
"gesture_anchors \"{0}\" tidak ada di anchors"
],
"gesture_model 必須是 null 或檔名": [
"gesture_model must be null or a file name",
"gesture_model harus null atau nama file"
],
"packaging 必須是物件或 null": [
"packaging must be an object or null",
"packaging harus berupa objek atau null"
],
"packaging.colors 必須是陣列": [
"packaging.colors must be an array",
"packaging.colors harus berupa array"
],
"packaging.colors 每一筆要有 name": [
"Each packaging.colors entry needs a name",
"Setiap data packaging.colors harus ada name"
],
"packaging.colors 的 status 只能是 {0}": [
"packaging.colors status can only be {0}",
"status di packaging.colors hanya boleh {0}"
],
"packaging.enabled 必須是 true/false": [
"packaging.enabled must be true/false",
"packaging.enabled harus true/false"
],
"packaging.model_source 不能參考自己": [
"packaging.model_source cannot reference itself",
"packaging.model_source tidak boleh merujuk ke dirinya sendiri"
],
"packaging.model_source 必須是 null 或專案名稱": [
"packaging.model_source must be null or a project name",
"packaging.model_source harus null atau nama proyek"
],
"packaging.region（地區）必須是非空字串": [
"packaging.region (Region) must be a non-empty string",
"packaging.region (Wilayah) harus string yang tidak kosong"
],
"packaging.style（型體）必須是非空字串": [
"packaging.style (Style) must be a non-empty string",
"packaging.style (Artikel) harus string yang tidak kosong"
],
"packaging.{0} 必須是字串": [
"packaging.{0} must be a string",
"packaging.{0} harus berupa string"
],
"project_name 必須是非空字串": [
"project_name must be a non-empty string",
"project_name harus string yang tidak kosong"
],
"reset_dwell_sec 必須大於 0": [
"reset_dwell_sec must be greater than 0",
"reset_dwell_sec harus lebih dari 0"
],
"reset_zone 必須是 [x, y, w, h] 或 null": [
"reset_zone must be [x, y, w, h] or null",
"reset_zone harus [x, y, w, h] atau null"
],
"reset_zone 與步驟 {0}「{1}」的 ROI 重疊": [
"reset_zone overlaps the ROI of step {0} \"{1}\"",
"reset_zone tumpang tindih dengan ROI langkah {0} \"{1}\""
],
"reset_zone 超出 resolution 範圍": [
"reset_zone is outside the resolution range",
"reset_zone di luar batas resolution"
],
"resolution 必須是 [寬, 高] 兩個正整數": [
"resolution must be [width, height], two positive integers",
"resolution harus [lebar, tinggi], dua bilangan bulat positif"
],
"rtsp://帳號:密碼@相機位址:554/stream1": [
"rtsp://user:password@camera-address:554/stream1",
"rtsp://user:sandi@alamat-kamera:554/stream1"
],
"schema_version 必須是 {0} 之一": [
"schema_version must be one of {0}",
"schema_version harus salah satu dari {0}"
],
"skip_alert_sec 必須大於 0": [
"skip_alert_sec must be greater than 0",
"skip_alert_sec harus lebih dari 0"
],
"source_kind 只能是 demo 或 camera": [
"source_kind can only be demo or camera",
"source_kind hanya boleh demo atau camera"
],
"state_anchor「{0}」不存在於 anchors": [
"state_anchor \"{0}\" does not exist in anchors",
"state_anchor \"{0}\" tidak ada di anchors"
],
"state_every_n_frames 必須是 ≥1 的整數": [
"state_every_n_frames must be an integer ≥1",
"state_every_n_frames harus bilangan bulat ≥1"
],
"state_fixed 必須是 [x, y, w, h] 或 null": [
"state_fixed must be [x, y, w, h] or null",
"state_fixed harus [x, y, w, h] atau null"
],
"state_fixed 超出 resolution 範圍": [
"state_fixed is outside the resolution range",
"state_fixed di luar batas resolution"
],
"state_rel 必須是 [rx, ry, rw, rh]": [
"state_rel must be [rx, ry, rw, rh]",
"state_rel harus [rx, ry, rw, rh]"
],
"steps 必須是陣列": [
"steps must be an array",
"steps harus berupa array"
],
"steps[{0}] 只有 hand_dwell 可以用 hand_and_visual": [
"steps[{0}]: only hand_dwell can use hand_and_visual",
"steps[{0}]: hanya hand_dwell yang boleh pakai hand_and_visual"
],
"steps[{0}] 必須是物件": [
"steps[{0}] must be an object",
"steps[{0}] harus berupa objek"
],
"steps[{0}].continuous 必須是 true/false": [
"steps[{0}].continuous must be true/false",
"steps[{0}].continuous harus true/false"
],
"steps[{0}].dwell_time_sec 必須大於 0": [
"steps[{0}].dwell_time_sec must be greater than 0",
"steps[{0}].dwell_time_sec harus lebih dari 0"
],
"steps[{0}].required 必須是 true/false": [
"steps[{0}].required must be true/false",
"steps[{0}].required harus true/false"
],
"steps[{0}].roi 必須是 [x, y, w, h]": [
"steps[{0}].roi must be [x, y, w, h]",
"steps[{0}].roi harus [x, y, w, h]"
],
"steps[{0}].roi 超出 resolution 範圍或寬高不是正數": [
"steps[{0}].roi is outside the resolution range or width/height is not positive",
"steps[{0}].roi di luar batas resolution atau lebar/tinggi bukan positif"
],
"steps[{0}].step_index 必須等於 {1}": [
"steps[{0}].step_index must equal {1}",
"steps[{0}].step_index harus sama dengan {1}"
],
"steps[{0}].step_name 必須是非空字串": [
"steps[{0}].step_name must be a non-empty string",
"steps[{0}].step_name harus string yang tidak kosong"
],
"steps[{0}].template_file 必須是非空字串": [
"steps[{0}].template_file must be a non-empty string",
"steps[{0}].template_file harus string yang tidak kosong"
],
"steps[{0}].timeout_sec 必須大於 0": [
"steps[{0}].timeout_sec must be greater than 0",
"steps[{0}].timeout_sec harus lebih dari 0"
],
"steps[{0}].trigger_mode 只能是 hand_only 或 hand_and_visual": [
"steps[{0}].trigger_mode can only be hand_only or hand_and_visual",
"steps[{0}].trigger_mode hanya boleh hand_only atau hand_and_visual"
],
"steps[{0}].type 只能是 {1}": [
"steps[{0}].type can only be {1}",
"steps[{0}].type hanya boleh {1}"
],
"steps[{0}].visual_match_min 必須是 0～1 的數字（hand_and_visual 必填）": [
"steps[{0}].visual_match_min must be a number 0–1 (required for hand_and_visual)",
"steps[{0}].visual_match_min harus angka 0–1 (wajib untuk hand_and_visual)"
],
"steps[{0}].visual_match_min 必須是 null 或 0～1 的數字": [
"steps[{0}].visual_match_min must be null or a number 0–1",
"steps[{0}].visual_match_min harus null atau angka 0–1"
],
"video_file 必須是非空字串": [
"video_file must be a non-empty string",
"video_file harus string yang tidak kosong"
],
"where 只能是 local 或 gpu": [
"where can only be local or gpu",
"where hanya boleh local atau gpu"
],
"work_area 必須是 [x, y, w, h] 或 null": [
"work_area must be [x, y, w, h] or null",
"work_area harus [x, y, w, h] atau null"
],
"zones 名稱重複：{0}": [
"Duplicate zones name: {0}",
"Nama zones duplikat: {0}"
],
"zones 必須是陣列": [
"zones must be an array",
"zones harus berupa array"
],
"zones[{0}] 必須是物件": [
"zones[{0}] must be an object",
"zones[{0}] harus berupa objek"
],
"zones[{0}] 沒有 anchor 就必須給 fixed [x, y, w, h]": [
"zones[{0}] without an anchor must have fixed [x, y, w, h]",
"zones[{0}] tanpa anchor harus diisi fixed [x, y, w, h]"
],
"zones[{0}].anchor「{1}」不存在於 anchors": [
"zones[{0}].anchor \"{1}\" does not exist in anchors",
"zones[{0}].anchor \"{1}\" tidak ada di anchors"
],
"zones[{0}].fixed 超出 resolution 範圍": [
"zones[{0}].fixed is outside the resolution range",
"zones[{0}].fixed di luar batas resolution"
],
"zones[{0}].index 必須是 null 或非負整數": [
"zones[{0}].index must be null or a non-negative integer",
"zones[{0}].index harus null atau bilangan bulat non-negatif"
],
"zones[{0}].name 必須是非空字串": [
"zones[{0}].name must be a non-empty string",
"zones[{0}].name harus string yang tidak kosong"
],
"zones[{0}].rel 必須是 [rx, ry, rw, rh] 且寬高 > 0": [
"zones[{0}].rel must be [rx, ry, rw, rh] with width/height > 0",
"zones[{0}].rel harus [rx, ry, rw, rh] dengan lebar/tinggi > 0"
],
"{0}  完成 {1} 輪  漏做 {2} 輪": [
"{0}  {1} cycles done  {2} cycles missed",
"{0}  {1} siklus selesai  {2} siklus terlewat"
],
"{0} {1} 秒，點一下跳到這裡": [
"{0} {1} s, click to jump here",
"{0} {1} detik, klik untuk lompat ke sini"
],
"{0} 分鐘前更新": [
"Updated {0} min ago",
"Diperbarui {0} menit lalu"
],
"{0} 小時前更新": [
"Updated {0} h ago",
"Diperbarui {0} jam lalu"
],
"{0} 張訂單：": [
"{0} orders: ",
"{0} order: "
],
"{0} 是 gesture 類型，但專案沒有設定 gesture_model": [
"{0} is a gesture type, but the project has no gesture_model set",
"{0} tipe gesture, tapi proyek belum diatur gesture_model"
],
"{0} 是後來才出題的。": [
"{0} was added to the test later.",
"{0} baru ditambahkan ke tes belakangan."
],
"{0} 有 {1} 條{2}線": [
"{0} has {1} {2} lines",
"{0} punya {1} lini {2}"
],
"{0} 段": [
"{0} segments",
"{0} segmen"
],
"{0} 漏 {1}": [
"{0} missed {1}",
"{0} terlewat {1}"
],
"{0} 秒前更新": [
"Updated {0} s ago",
"Diperbarui {0} detik lalu"
],
"{0} 秒（{1} / {2} 格）": [
"{0} s ({1} / {2} frames)",
"{0} detik ({1} / {2} frame)"
],
"{0} 第 {1} 段": [
"{0} segment {1}",
"{0} segmen {1}"
],
"{0} 第 {1} 段 {2} 到 {3}": [
"{0} segment {1} {2} to {3}",
"{0} segmen {1} {2} sampai {3}"
],
"{0} 輪・漏做 {1} 輪": [
"{0} cycles · {1} missed",
"{0} siklus · {1} terlewat"
],
"{0} 輪平均": [
"{0}-cycle average",
"Rata-rata {0} siklus"
],
"{0} 輪，左舊右新　✕ 漏做　! 超時": [
"{0} cycles, oldest left, newest right　✕ Missed　! Overtime",
"{0} siklus, lama di kiri, baru di kanan　✕ Terlewat　! Lewat waktu"
],
"{0} 還沒設定相機，請到「產線設定」填相機來源": [
"{0} has no camera set yet, go to \"Line settings\" and enter the camera source",
"{0} belum diatur kameranya, buka \"Pengaturan lini\" dan isi sumber kamera"
],
"{0} 雙": [
"{0} pairs",
"{0} pasang"
],
"{0}.count 只能是 any 或 all": [
"{0}.count can only be any or all",
"{0}.count hanya boleh any atau all"
],
"{0}.label 必須是非空字串": [
"{0}.label must be a non-empty string",
"{0}.label harus string yang tidak kosong"
],
"{0}.label（物品名稱）必須是非空字串": [
"{0}.label (item name) must be a non-empty string",
"{0}.label (nama barang) harus string yang tidak kosong"
],
"{0}.label（狀態名稱）必須是非空字串": [
"{0}.label (state name) must be a non-empty string",
"{0}.label (nama status) harus string yang tidak kosong"
],
"{0}.min_overlap 必須在 0～1": [
"{0}.min_overlap must be within 0–1",
"{0}.min_overlap harus di antara 0–1"
],
"{0}.min_prob 必須在 0～1": [
"{0}.min_prob must be within 0–1",
"{0}.min_prob harus di antara 0–1"
],
"{0}.object「{1}」不存在於 anchors": [
"{0}.object \"{1}\" does not exist in anchors",
"{0}.object \"{1}\" tidak ada di anchors"
],
"{0}.object「{1}」不存在於 anchors，也不是任何 item 步驟的物品": [
"{0}.object \"{1}\" does not exist in anchors and is not an item of any item step",
"{0}.object \"{1}\" tidak ada di anchors dan bukan barang dari langkah item mana pun"
],
"{0}.zone「{1}」不存在於 zones": [
"{0}.zone \"{1}\" does not exist in zones",
"{0}.zone \"{1}\" tidak ada di zones"
],
"{0}:{1} 開始監控": [
"Monitoring started at {0}:{1}",
"Mulai pantau {0}:{1}"
],
"{0}x{1} 不同，固定座標／work_area 可能對不上": [
"{0}x{1} differ; fixed coordinates / work_area may not match",
"{0}x{1} berbeda; koordinat tetap / work_area mungkin tidak cocok"
],
"{0}–{1} 秒": [
"{0}–{1} s",
"{0}–{1} detik"
],
"{0}　{1}　{2} 步": [
"{0}　{1}　{2} steps",
"{0}　{1}　{2} langkah"
],
"{0}　手框 {1}／自動 {2}": [
"{0}　manual {1} / auto {2}",
"{0}　manual {1} / otomatis {2}"
],
"{0}（你輸入的是「{1}」）": [
"{0} (you entered \"{1}\")",
"{0} (yang kamu isi: \"{1}\")"
],
"{0}（還沒設定型體地區）": [
"{0} (Style/Region not set yet)",
"{0} (Artikel/Wilayah belum diatur)"
],
"{0}（點一下跳過去）": [
"{0} (click to jump there)",
"{0} (klik untuk lompat ke sana)"
],
"{0}，要 ≥ {1}）。範圍縮到手真的在碰的那幾秒，或先把被碰的物品框好。": [
"{0}, need ≥ {1}). Narrow the range to the seconds when the hand really touches it, or box the touched item first.",
"{0}, perlu ≥ {1}). Persempit rentang ke detik saat tangan benar-benar menyentuh, atau kotak dulu barang yang disentuh."
],
"{0}：找到率 {1} → {2}，掉 {3} 點": [
"{0}: find rate {1} → {2}, down {3} pts",
"{0}: tingkat temuan {1} → {2}, turun {3} poin"
],
"{0}：漏做 {1} 次": [
"{0}: missed {1} times",
"{0}: terlewat {1} kali"
],
"{0}：空桌誤報 {1} 格 → {2} 格（{3} → {4}）": [
"{0}: empty-desk false alarms {1} frames → {2} frames ({3} → {4})",
"{0}: alarm palsu meja kosong {1} frame → {2} frame ({3} → {4})"
],
"‹ 回到上一步：框物品": [
"‹ Back: Box items",
"‹ Kembali: Beri kotak barang"
],
"‹ 回到上一步：空桌面": [
"‹ Back: Empty desk",
"‹ Kembali: Meja kosong"
],
"①②③＝順序": [
"①②③ = order",
"①②③ = urutan"
],
"✓ {0} 秒": [
"✓ {0} s",
"✓ {0} detik"
],
"　{0} 格": [
"　{0} frames",
"　{0} frame"
],
"　{0}{1}　{2}　{3}　模型 {4}　{5}": [
"　{0}{1}　{2}　{3}　model {4}　{5}",
"　{0}{1}　{2}　{3}　model {4}　{5}"
],
"　合成配色多加 {0} 張": [
"　+{0} images from color synthesis",
"　+{0} gambar dari sintesis warna"
],
"　已 {0} 分 {1} 秒": [
"　{0} min {1} s elapsed",
"　sudah {0} menit {1} detik"
],
"　已用 {0} 秒": [
"　{0} s used",
"　Sudah {0} detik"
],
"　手碰：{0}": [
"　Hand touch: {0}",
"　Sentuhan tangan: {0}"
],
"　本機 {0}": [
"　Local {0}",
"　Lokal {0}"
],
"　正在做：{0}": [
"　Doing: {0}",
"　Sedang dikerjakan: {0}"
],
"　還沒做：{0}": [
"　Not done yet: {0}",
"　Belum dikerjakan: {0}"
],
"　錄製中 {0} 格": [
"　Recording {0} frames",
"　Merekam {0} frame"
],
"。程式一開會自動由舊到新補送；按「立即上傳」現在就一起送。": [
". When the program starts it sends them automatically, oldest first; press \"Upload now\" to send them now.",
". Saat program dibuka, data dikirim otomatis dari yang lama ke yang baru; tekan \"Upload sekarang\" untuk kirim sekarang."
],
"「{0}」{1} 段（還差 {2} 段）": [
"\"{0}\" {1} segments ({2} more needed)",
"\"{0}\" {1} segmen (kurang {2} segmen)"
],
"「{0}」信心 ≥ {1}、面積 ≥ 桌面 {2}%": [
"\"{0}\" confidence ≥ {1}, area ≥ {2}% of desk",
"\"{0}\" keyakinan ≥ {1}, luas ≥ {2}% area meja"
],
"「{0}」失敗：{1}": [
"\"{0}\" failed: {1}",
"\"{0}\" gagal: {1}"
],
"「{0}」找到 {1} 個型體、{2} 個包裝方式（地區）": [
"\"{0}\": found {1} styles, {2} packing methods (regions)",
"\"{0}\": ketemu {1} artikel, {2} metode kemas (wilayah)"
],
"「{0}」是動作，不用畫框": [
"\"{0}\" is an action, no box needed",
"\"{0}\" adalah gerakan, tidak perlu kotak"
],
"「{0}」是動作，不用畫框，只要在時間軸上拉範圍。": [
"\"{0}\" is an action. No box needed, just drag a range on the timeline.",
"\"{0}\" adalah gerakan. Tidak perlu gambar kotak, cukup tarik rentang di timeline."
],
"「{0}」正在產線監控中，先到監控畫面停止，再載入": [
"\"{0}\" is being monitored on the line. Stop it on the Monitor screen first, then load",
"\"{0}\" sedang dipantau di lini. Hentikan dulu di layar pantau, lalu muat"
],
"「{0}」正在監控、訓練或錄影，不能刪除": [
"\"{0}\" is being monitored, trained or recorded and cannot be deleted",
"\"{0}\" sedang dipantau, dilatih, atau direkam, tidak bisa dihapus"
],
"「{0}」沒有停用，不能刪除": [
"\"{0}\" is not disabled and cannot be deleted",
"\"{0}\" belum dinonaktifkan, tidak bisa dihapus"
],
"「{0}」產線 {1} 正在用，不能刪除": [
"\"{0}\" is in use by line {1} and cannot be deleted",
"\"{0}\" sedang dipakai lini {1}, tidak bisa dihapus"
],
"「{0}」的「{1}」": [
"\"{1}\" in \"{0}\"",
"\"{1}\" di \"{0}\""
],
"「{0}」的停留秒數不是數字": [
"Dwell seconds for \"{0}\" is not a number",
"Detik tahan untuk \"{0}\" bukan angka"
],
"「{0}」的停留秒數要在 0.1～10 秒": [
"Dwell seconds for \"{0}\" must be 0.1–10 s",
"Detik tahan untuk \"{0}\" harus 0.1–10 detik"
],
"「{0}」的模型被 {1} 參考，不能刪除": [
"The model of \"{0}\" is used by {1}, so it cannot be deleted",
"Model \"{0}\" dipakai oleh {1}, tidak bisa dihapus"
],
"「{0}」的目前版本改成 {1}": [
"Current version of \"{0}\" changed to {1}",
"Versi aktif \"{0}\" diganti ke {1}"
],
"「{0}」的辨識物品「{1}」不在模型認得的物品裡（{2}）": [
"Item \"{1}\" for \"{0}\" is not one the model knows ({2})",
"Barang \"{1}\" untuk \"{0}\" tidak dikenal model ({2})"
],
"「{0}」要選辨識物品": [
"Choose an item to detect for \"{0}\"",
"Pilih barang yang dideteksi untuk \"{0}\""
],
"「{0}」還有段落，先把段落刪掉才能刪名稱": [
"\"{0}\" still has segments. Delete the segments before deleting the name",
"\"{0}\" masih punya segmen. Hapus segmennya dulu baru hapus nama"
],
"・手碰 {0}": [
"・Hand touch {0}",
"・Sentuhan tangan {0}"
],
"・未框": [
"・No box",
"・Belum ada kotak"
],
"・本站完成 {0} 輪": [
" · This station completed {0} cycles",
" · Stasiun ini selesai {0} siklus"
],
"・舊版 {0} 格": [
"・Old version {0} frames",
"・Versi lama {0} frame"
],
"上一處": [
"Previous",
"Sebelumnya"
],
"上一輪已結算": [
"Previous cycle closed",
"Siklus sebelumnya sudah ditutup"
],
"上一輪的物品一直留在畫面上（可能卡住），清空後才會開始下一輪": [
"Items from the last cycle are still on screen (maybe stuck); the next cycle starts once they are cleared",
"Barang dari siklus sebelumnya masih di layar (mungkin macet); siklus berikutnya mulai setelah dibersihkan"
],
"上傳": [
"Upload",
"Unggah"
],
"上傳中…": [
"Uploading…",
"Mengunggah…"
],
"上傳到共用硬碟": [
"Upload to shared drive",
"Unggah ke drive bersama"
],
"上傳成共用硬碟的新版本": [
"Upload as a new version on the shared drive",
"Unggah sebagai versi baru di drive bersama"
],
"上傳這台電腦的專案": [
"Upload this computer's projects",
"Unggah proyek komputer ini"
],
"上傳：": [
"Upload: ",
"Upload: "
],
"上傳＝在共用硬碟新增一版（舊版都留著，不會被蓋掉），並設成目前版本。別人在你載入之後又傳過時，會先問要不要設成目前版本。沒有模型的專案也能上傳，讓別台電腦拿去訓練。": [
"Upload = add a new version on the shared drive (old versions are kept, never overwritten) and make it the current version. If someone else uploaded after you loaded, you are asked first whether to make yours current. Projects without a model can be uploaded too, so another computer can train them.",
"Unggah = tambah versi baru di drive bersama (versi lama tetap disimpan, tidak ditimpa) dan jadikan versi saat ini. Kalau orang lain sudah unggah setelah Anda memuat, akan ditanya dulu apakah mau dijadikan versi saat ini. Proyek tanpa model juga bisa diunggah supaya komputer lain bisa melatihnya."
],
"上次用的": [
"Last used",
"Terakhir dipakai"
],
"上次的模型訓練時看過這幾項的考題：{0}。這次的比較會偏向上次；下一次訓練起就公平。": [
"The previous model saw test items for these during training: {0}. This comparison favors the previous model; it will be fair from the next training on.",
"Model sebelumnya sudah melihat soal tes untuk ini saat dilatih: {0}. Perbandingan kali ini condong ke model sebelumnya; mulai latihan berikutnya akan adil."
],
"上次的模型：{0} 訓練。": [
"Previous model: trained {0}.",
"Model sebelumnya: dilatih {0}."
],
"上線前先錄 2～3 輪做離線驗證；在那之前監控算試跑": [
"Record 2–3 cycles for offline verification before going live; until then monitoring is a trial run",
"Sebelum dipakai, rekam 2–3 siklus untuk verifikasi offline; sebelum itu pemantauan hanya uji coba"
],
"上限 {0} 秒": [
"Limit {0} s",
"Batas {0} detik"
],
"下一步：框物品 ›": [
"Next: Box items ›",
"Berikutnya: Beri kotak barang ›"
],
"下一步：標動作 ›": [
"Next: Mark actions ›",
"Berikutnya: Tandai gerakan ›"
],
"下一處": [
"Next",
"Berikutnya"
],
"不用任何標註：分析示範影片裡每一輪都重複的動作，列出候選步驟讓你挑": [
"No labels needed: finds actions repeated in every cycle of the demo video and lists them as candidate steps for you to pick",
"Tanpa label: mencari gerakan yang berulang di setiap siklus video contoh dan menampilkannya sebagai kandidat langkah untuk dipilih"
],
"不能參考自己的模型": [
"Cannot use its own model as reference",
"Tidak bisa pakai model sendiri sebagai referensi"
],
"不能啟動監控": [
"Cannot start monitoring",
"Tidak bisa mulai pantau"
],
"不認得的動作：{0}": [
"Unknown action: {0}",
"Gerakan tidak dikenal: {0}"
],
"不響": [
"Off",
"Mati"
],
"主機喇叭": [
"Host speaker",
"Speaker PC host"
],
"主機蜂鳴器": [
"Host buzzer",
"Buzzer host"
],
"主鍵＝型體＋地區，兩個合起來不能重複。型體照規定填「6 碼數字＋空一格＋2 碼數字」，例如 310222 01。客戶只是顯示用。": [
"Key = Style + Region; the combination must be unique. Enter Style as \"6 digits + space + 2 digits\", e.g. 310222 01. Customer is for display only.",
"Kunci = Artikel + Wilayah; gabungannya tidak boleh dobel. Isi Artikel dengan format \"6 angka + spasi + 2 angka\", contoh 310222 01. Customer hanya untuk tampilan."
],
"今天要做的": [
"To do today",
"Dikerjakan hari ini"
],
"今天這條線還沒有用相機監控的紀錄": [
"No camera monitoring records for this line today yet",
"Belum ada catatan pantau kamera untuk lini ini hari ini"
],
"今日報工": [
"reported today",
"laporan hari ini"
],
"今日目標": [
"target today",
"target hari ini"
],
"今日統計": [
"Today's stats",
"Statistik hari ini"
],
"今日統計　{0}{1}（{2}）　{3}": [
"Today's stats　{0}{1} ({2})　{3}",
"Statistik hari ini　{0}{1} ({2})　{3}"
],
"仍要換上新模型": [
"Use the new model anyway",
"Tetap pakai model baru"
],
"任一物品找到率掉 {0} 點以上而且至少少 {1} 格，或空桌誤報升 {2} 點以上而且至少多 {3} 格，整次算變差。": [
"If any item's find rate drops by {0}+ pts and at least {1} frames fewer, or empty-desk false alarms rise by {2}+ pts and at least {3} frames more, the whole run counts as worse.",
"Jika tingkat temuan barang mana pun turun {0} poin atau lebih dan minimal kurang {1} frame, atau alarm palsu meja kosong naik {2} poin atau lebih dan minimal tambah {3} frame, seluruh hasil dihitung lebih buruk."
],
"伺服器正在訓練另一個專案「{0}」，請等它完成": [
"The server is training another project \"{0}\". Please wait until it finishes",
"Server sedang melatih proyek lain \"{0}\". Tunggu sampai selesai"
],
"作業員開始做任何一個步驟，就計入第 {0} 輪": [
"When the worker starts any step, it counts as cycle {0}",
"Saat operator mulai langkah apa pun, dihitung sebagai siklus {0}"
],
"使用中的產線": [
"Lines in use",
"Lini yang dipakai"
],
"來源沒有送出任何畫面（相機連不上，或示範影片讀不到）": [
"Source sent no frames (camera cannot connect, or demo video cannot be read)",
"Sumber tidak mengirim gambar (kamera tidak tersambung, atau video contoh tidak terbaca)"
],
"例如 310222 01": [
"e.g. 310222 01",
"contoh: 310222 01"
],
"例如 A 站": [
"e.g. Station A",
"mis. Stasiun A"
],
"例如 \\\\NAS01\\SOP-Guard\\projects": [
"e.g. \\\\NAS01\\SOP-Guard\\projects",
"mis. \\\\NAS01\\SOP-Guard\\projects"
],
"例如 全白": [
"e.g. All white",
"contoh: Putih semua"
],
"例如 加了白鞋的框": [
"e.g. added boxes for white shoes",
"mis. tambah kotak untuk sepatu putih"
],
"例如 包裝 1 線": [
"e.g. Packing line 1",
"mis. Lini kemas 1"
],
"例如 歐洲": [
"e.g. Europe",
"contoh: Eropa"
],
"例如「檢查鞋舌」：先到「物品」把鞋舌框成一個物品，再拉這個動作的範圍。手同時碰到鞋子和鞋舌時，系統取框比較小的鞋舌。鞋舌這個物品步驟可以到「包裝方式設定」關掉必要，重新排步驟也會照舊。": [
"For example \"Check tongue\": first go to \"Items\" and box the tongue as an item, then drag the range for this action. When the hand touches both the shoe and the tongue, the system picks the smaller box (the tongue). The tongue item step can be set as not required in \"Packing method settings\", and it stays that way when steps are reordered.",
"Contoh \"Cek lidah sepatu\": buka \"Barang\" dulu dan beri kotak lidah sepatu sebagai barang, lalu tarik rentang gerakan ini. Kalau tangan menyentuh sepatu dan lidah sepatu sekaligus, sistem memilih kotak yang lebih kecil (lidah sepatu). Langkah barang lidah sepatu bisa dimatikan sebagai wajib di \"Pengaturan metode kemas\", dan tetap begitu walau langkah diurutkan ulang."
],
"例如「檢查鞋舌」：先到「物品」把鞋舌框成一個物品，再拉這個動作的範圍。手同時碰到鞋子和鞋舌時，系統取框比較小的鞋舌。鞋舌這個物品步驟可以到「包裝明細」關掉必要，重新排步驟也會照舊。": [
"For example \"Check tongue\": first go to \"Items\" and box the tongue as an item, then drag the range for this action. When the hand touches both the shoe and the tongue, the system picks the smaller box (the tongue). The tongue item step can be set as not required in \"Packing details\", and it stays that way when steps are reordered.",
"Contoh \"Cek lidah sepatu\": buka \"Barang\" dulu dan beri kotak lidah sepatu sebagai barang, lalu tarik rentang gerakan ini. Kalau tangan menyentuh sepatu dan lidah sepatu sekaligus, sistem memilih kotak yang lebih kecil (lidah sepatu). Langkah barang lidah sepatu bisa dimatikan sebagai wajib di \"Rincian kemas\", dan tetap begitu walau langkah diurutkan ulang."
],
"依序模式": [
"Sequential mode",
"Mode berurutan"
],
"依片段分組交叉驗證（{0} 組）整體正確率 = {1}（{2} 個視窗）": [
"Grouped-by-clip cross validation ({0} groups) overall accuracy = {1} ({2} windows)",
"Validasi silang per klip ({0} grup) akurasi total = {1} ({2} jendela)"
],
"保留上次的模型": [
"Keep the previous model",
"Tetap pakai model sebelumnya"
],
"候選步驟": [
"Candidate steps",
"Kandidat langkah"
],
"做完的樣子，例如 盒端貼紙": [
"What it looks like when done, e.g. box-end sticker",
"Bentuk saat selesai, contoh: stiker ujung kotak"
],
"停止監控": [
"Stop monitoring",
"Berhenti pantau"
],
"停止錄製，存成示範影片": [
"Stop recording and save as demo video",
"Berhenti merekam, simpan sebagai video contoh"
],
"停用": [
"Disable",
"Nonaktifkan"
],
"停用的包裝方式": [
"Disabled packing methods",
"Metode kemas nonaktif"
],
"停用的包裝方式（啟用／刪除）": [
"Disabled packing methods (enable / delete)",
"Metode kemas nonaktif (aktifkan / hapus)"
],
"停留秒數": [
"Hold time (s)",
"Lama diam (detik)"
],
"偵測範圍（整張桌面）": [
"Detection area (whole desk)",
"Area deteksi (seluruh meja)"
],
"像「{0}」的「{1}」（{2}% 的畫面）": [
"Looks like \"{1}\" in \"{0}\" ({2}% of frames)",
"Mirip \"{1}\" di \"{0}\" ({2}% bingkai)"
],
"儲存": [
"Save",
"Simpan"
],
"儲存並讀取": [
"Save and load",
"Simpan dan baca"
],
"儲存這一段": [
"Save this segment",
"Simpan segmen ini"
],
"先不要": [
"Not now",
"Nanti saja"
],
"先在上面填共用硬碟資料夾": [
"Enter the shared drive folder above first",
"Isi dulu folder drive bersama di atas"
],
"先在右邊點一個名稱（或新增一個）": [
"First click a name on the right (or add one)",
"Klik dulu satu nama di kanan (atau tambah baru)"
],
"先在時間軸上點一段": [
"First click a segment on the timeline",
"Klik dulu satu segmen di timeline"
],
"先填廠別": [
"Enter the Factory first",
"Isi Pabrik dulu"
],
"先存好至少一段物品，才能標動作": [
"Save at least one item segment before marking actions",
"Simpan minimal satu segmen barang dulu sebelum menandai gerakan"
],
"先有一段示範影片": [
"A demo video is needed first",
"Perlu video contoh dulu"
],
"先框好一樣物品，再標動作": [
"Box an item first, then label actions",
"Beri kotak satu barang dulu, baru tandai gerakan"
],
"先標至少一格空桌面": [
"Mark at least one empty-desk frame first",
"Tandai minimal satu bingkai meja kosong dulu"
],
"先輸入名稱再按新增": [
"Enter a name first, then click Add",
"Isi nama dulu, lalu klik Tambah"
],
"內容不是 JSON": [
"Content is not JSON",
"Isi bukan JSON"
],
"全部": [
"All",
"Semua"
],
"共 {0} 個": [
"{0} in total",
"Total {0}"
],
"共 {0} 次": [
"{0} times total",
"Total {0} kali"
],
"共用硬碟": [
"Shared drive",
"Drive bersama"
],
"共用硬碟上「{0}」v{1} 的模型檔壞了（best.pt 不是完整的檔案），沒有載入": [
"Model file for \"{0}\" v{1} on the shared drive is broken (best.pt is incomplete), not loaded",
"File model \"{0}\" v{1} di drive bersama rusak (best.pt tidak lengkap), tidak dimuat"
],
"共用硬碟上「{0}」沒有 v{1}": [
"\"{0}\" has no v{1} on the shared drive",
"\"{0}\" tidak punya v{1} di drive bersama"
],
"共用硬碟上有 {0} 個專案": [
"{0} projects on the shared drive",
"Ada {0} proyek di drive bersama"
],
"共用硬碟上沒有「{0}」": [
"\"{0}\" is not on the shared drive",
"\"{0}\" tidak ada di drive bersama"
],
"共用硬碟上還沒有專案": [
"No projects on the shared drive yet",
"Belum ada proyek di drive bersama"
],
"共用硬碟有新版": [
"New version on shared drive",
"Ada versi baru di drive bersama"
],
"共用硬碟沒有": [
"Not on shared drive",
"Tidak ada di drive bersama"
],
"共用硬碟目前": [
"Shared drive current",
"Drive bersama saat ini"
],
"共用硬碟資料夾（這台電腦記住，之後不用再填）": [
"Shared drive folder (remembered on this computer)",
"Folder drive bersama (diingat di komputer ini)"
],
"共用硬碟（載入／上傳專案）": [
"Shared drive (load/upload projects)",
"Drive bersama (muat/unggah proyek)"
],
"其他": [
"Other",
"Lainnya"
],
"出現 {0} 次，平均 {1} 秒": [
"Seen {0} times, {1} s on average",
"Muncul {0} kali, rata-rata {1} dtk"
],
"分析動作：{0}/{1} 格": [
"Analysing actions: {0}/{1} frames",
"Menganalisis gerakan: {0}/{1} bingkai"
],
"分析步驟": [
"Analyze steps",
"Analisis langkah"
],
"分段裡偵測不到手，無法訓練": [
"No hands detected in the segments, cannot train",
"Tangan tidak terdeteksi di segmen, tidak bisa latih"
],
"判斷手碰到哪個物品中…": [
"Checking which item the hand touches…",
"Mengecek barang mana yang disentuh tangan…"
],
"刪了不能復原": [
"This cannot be undone",
"Tidak bisa dibatalkan"
],
"刪除": [
"Delete",
"Hapus"
],
"刪除「{0}」第 {1} 段（{2} – {3}）？": [
"Delete \"{0}\" segment {1} ({2} – {3})?",
"Hapus \"{0}\" segmen {1} ({2} – {3})?"
],
"刪除勾選的": [
"Delete selected",
"Hapus yang dipilih"
],
"刪除勾選的（{0}）": [
"Delete selected ({0})",
"Hapus yang dipilih ({0})"
],
"刪除名稱「{0}」？": [
"Delete name \"{0}\"?",
"Hapus nama \"{0}\"?"
],
"刪除這一段": [
"Delete this segment",
"Hapus segmen ini"
],
"刪除這個名稱（還沒有段落才能刪）": [
"Delete this name (only when it has no segments)",
"Hapus nama ini (hanya bisa jika belum ada segmen)"
],
"刪除＝把這台電腦上的專案資料夾（設定、步驟、框、影片、模型）整個刪掉，不能復原。共用硬碟上傳過的版本不會被刪。產線正在用、或別的包裝方式參考它的模型時不能刪。": [
"Delete = remove the whole project folder on this computer (settings, steps, boxes, video, model). This cannot be undone. Versions uploaded to the shared drive are not deleted. A method cannot be deleted while a line is using it or another packing method uses its model.",
"Hapus = menghapus seluruh folder proyek di komputer ini (pengaturan, langkah, kotak, video, model). Tidak bisa dibatalkan. Versi yang sudah diunggah ke drive bersama tidak ikut terhapus. Tidak bisa dihapus selama lini masih memakainya atau metode kemas lain memakai modelnya."
],
"到包裝方式設定": [
"Go to Packing method settings",
"Ke Pengaturan metode kemas"
],
"到包裝明細": [
"Go to Packing details",
"Ke Rincian kemas"
],
"到包裝設定（訓練）": [
"Go to Packing setup (training)",
"Ke Pengaturan kemas (latih)"
],
"到標記頁補框": [
"Add boxes on the label page",
"Tambah kotak di halaman tandai"
],
"到標記頁補框（{0} 處）": [
"Add boxes on the label page ({0} places)",
"Tambah kotak di halaman tandai ({0} tempat)"
],
"到監控畫面": [
"Go to Monitor screen",
"Ke Layar pantau"
],
"前往監控": [
"Go to Monitor",
"Ke Pantau"
],
"剛訓練好的「{0}」還沒排到這條線。要開始做它時按「操作 ▾ → 換包裝方式」，清單裡已幫你選好，按確認就好。": [
"The newly trained \"{0}\" is not scheduled on this line yet. When you start it, press \"Actions ▾ → Change packing method\"; it is already selected in the list, just press Confirm.",
"\"{0}\" yang baru dilatih belum dijadwalkan di lini ini. Saat mau mulai, tekan \"Aksi ▾ → Ganti metode kemas\"; sudah dipilihkan di daftar, tinggal tekan Konfirmasi."
],
"加入": [
"Add",
"Tambah"
],
"加入指定型體地區的素材": [
"Add material from a specific Style/Region",
"Tambah materi dari Artikel/Wilayah tertentu"
],
"動作": [
"Actions",
"Gerakan"
],
"動作只要拉時間範圍，不用畫框。": [
"For actions, just drag a time range. No box needed.",
"Untuk gerakan, cukup tarik rentang waktu. Tidak perlu gambar kotak."
],
"動作：只拉時間範圍，不畫框；要先框好被碰的物品。沒有要看手的步驟就跳過，直接訓練": [
"Actions: drag a time range only, no box; box the touched item first. If no step needs hand checking, skip this and train directly",
"Gerakan: hanya tarik rentang waktu, tanpa kotak; beri kotak barang yang disentuh dulu. Kalau tidak ada langkah yang perlu cek tangan, lewati dan langsung latih"
],
"動作：手碰到「{0}」": [
"Action: hand touches \"{0}\"",
"Gerakan: tangan menyentuh \"{0}\""
],
"勾選": [
"Select",
"Pilih"
],
"勾選的候選都要取名字": [
"Every ticked candidate needs a name",
"Setiap kandidat yang dicentang harus diberi nama"
],
"勾選的片段裡沒有任何框": [
"The selected clips have no boxes",
"Klip yang dipilih tidak punya kotak"
],
"勾選要留下的步驟並取名；同一個步驟出現在兩個候選時取同一個名字就會合併。點縮圖可跳到那一格。 綠色標籤＝跟其他專案取過名的步驟很像，名字已經先填好、勾起來了，請看縮圖確認。沒勾的（伸手、轉身這類過場）會當反例，教模型「手在畫面上不一定在做步驟」。": [
"Tick the steps to keep and name them; give two candidates the same name to merge them. Click a thumbnail to jump to that frame. Green tag = very similar to a step named in another project; the name is pre-filled and ticked, please check the thumbnails. Unticked ones (reaching, turning and other transitions) become negatives that teach the model \"hands on screen are not always doing a step\".",
"Centang langkah yang ingin disimpan dan beri nama; beri nama yang sama pada dua kandidat untuk menggabungkannya. Klik gambar kecil untuk lompat ke bingkai itu. Label hijau = sangat mirip langkah yang sudah dinamai di proyek lain; nama sudah diisi dan dicentang, periksa gambar kecilnya. Yang tidak dicentang (meraih, berbalik, dan transisi lain) menjadi contoh negatif yang mengajari model \"tangan di layar belum tentu sedang melakukan langkah\"."
],
"勾選＝拿這一輪的框選來訓練": [
"Checked = use this cycle's boxes for training",
"Dicentang = pakai kotak siklus ini untuk latih"
],
"包裝 1 線": [
"Packing line 1",
"Lini kemas 1"
],
"包裝方式": [
"Packing method",
"Metode kemas"
],
"包裝方式已停用": [
"Packing method is disabled",
"Metode kemas dinonaktifkan"
],
"包裝方式的辨識模型還沒訓練": [
"Recognition model for the packing method is not trained yet",
"Model pengenalan untuk metode kemas belum dilatih"
],
"包裝方式設定": [
"Packing method settings",
"Pengaturan metode kemas"
],
"包裝方式載入失敗：{0}": [
"Failed to load packing method: {0}",
"Gagal memuat metode kemas: {0}"
],
"包裝方式還沒有步驟": [
"Packing method has no steps yet",
"Metode kemas belum punya langkah"
],
"包裝明細": [
"Packing details",
"Rincian kemas"
],
"包裝設定（訓練）": [
"Packing setup (training)",
"Pengaturan kemas (latih)"
],
"匯入 GPU 訓練好的模型：": [
"Import model trained on GPU:",
"Impor model hasil latih GPU:"
],
"匯入並驗證": [
"Import and verify",
"Impor dan verifikasi"
],
"原包裝方式": [
"Original packing method",
"Metode kemas asal"
],
"參考": [
"Reference ",
"Referensi "
],
"參考 {0}（{1}）": [
"Reference {0} ({1})",
"Referensi {0} ({1})"
],
"參考來源「{0}」自己還沒有訓練好的模型": [
"Reference source \"{0}\" has no trained model yet",
"Sumber referensi \"{0}\" belum punya model yang dilatih"
],
"取消": [
"Cancel",
"Batal"
],
"取消分析": [
"Cancel analysis",
"Batal analisis"
],
"取消這一格": [
"Remove this frame",
"Hapus bingkai ini"
],
"只列有框選的": [
"Only show boxed ones",
"Hanya yang ada kotak"
],
"只持續 {0} 秒": [
"Lasted only {0} s",
"Hanya {0} detik"
],
"只接受 mp4／avi／mov／mkv": [
"Only mp4／avi／mov／mkv accepted",
"Hanya terima mp4／avi／mov／mkv"
],
"只有這台電腦載入 {0}（試跑用，不改目前版本）": [
"Load {0} on this computer only (for trial, current version not changed)",
"Muat {0} hanya di komputer ini (untuk uji coba, versi aktif tidak diubah)"
],
"只用本型體地區的素材": [
"Only use material from this Style/Region",
"Hanya pakai materi Artikel/Wilayah ini"
],
"只看自動框": [
"Only auto boxes",
"Hanya kotak otomatis"
],
"只算完成的輪": [
"Completed cycles only",
"Hanya siklus yang selesai"
],
"只算這台電腦、只算相機監控（示範影片不算）。每個包裝方式一列，一天只記總數。程式一開、每 10 分鐘、停止監控、換線時上傳到 EIP，還沒傳成功的日子一起補送；同一天重送會覆蓋。上傳到 EIP 的只有各步驟的漏做、超時次數，完成和漏做輪數只留本機。": [
"Only this PC and only camera monitoring (demo videos not counted). One row per packing method, one total per day. Uploaded to EIP when the program starts, every 10 minutes, on stop monitoring and on line change; days not yet uploaded are sent together; resending the same day overwrites it. Only missed and overtime counts per step go to EIP; completed and missed cycle counts stay on this PC.",
"Hanya PC ini dan hanya pantau kamera (video contoh tidak dihitung). Satu baris per metode kemas, satu total per hari. Diupload ke EIP saat program dibuka, tiap 10 menit, saat berhenti pantau dan saat ganti lini; hari yang belum terkirim dikirim bersama; kirim ulang hari yang sama akan menimpa. Yang diupload ke EIP hanya jumlah terlewat dan lewat waktu per langkah; jumlah siklus selesai dan terlewat hanya disimpan di PC ini."
],
"可以打 12.4、0:12.4 或 00:12.4": [
"You can type 12.4, 0:12.4 or 00:12.4",
"Bisa ketik 12.4, 0:12.4 atau 00:12.4"
],
"可以直接上線": [
"Ready to go live",
"Siap dipakai"
],
"可編輯欄位（改了直接存）": [
"Editable fields (saved on change)",
"Kolom yang bisa diubah (langsung tersimpan)"
],
"可能是過場動作": [
"Possibly a transition",
"Mungkin gerakan transisi"
],
"右邊先新增動作": [
"Add an action on the right first",
"Tambah gerakan di kanan dulu"
],
"右邊先新增物品": [
"Add an item on the right first",
"Tambah barang di kanan dulu"
],
"右邊點一個名稱": [
"Click a name on the right",
"Klik satu nama di kanan"
],
"各步驟漏做／超時（上傳到 EIP 的就是這欄）": [
"Missed / overtime per step (this column is what goes to EIP)",
"Terlewat / lewat waktu per langkah (kolom ini yang diupload ke EIP)"
],
"合成配色": [
"Color synthesis",
"Sintesis warna"
],
"合成配色中…": [
"Generating color variants…",
"Membuat variasi warna…"
],
"合成配色：{0}（多加 {1} 張）\\n": [
"Synthetic colorways: {0} ({1} extra images)\\n",
"Warna sintetis: {0} (tambah {1} gambar)\\n"
],
"同一個型體的每個地區各一列；只列有步驟、有模型、啟用中的": [
"One row per region of the same style; only active ones with steps and a model",
"Satu baris per wilayah dari artikel yang sama; hanya yang aktif, punya langkah dan model"
],
"同版本": [
"Same version",
"Versi sama"
],
"名字是照相似度預填的，請看縮圖確認": [
"The name was pre-filled by similarity; please check the thumbnails",
"Nama diisi otomatis berdasarkan kemiripan; periksa gambar kecilnya"
],
"名稱": [
"Name",
"Nama"
],
"名稱「{0}」不存在，請重新整理": [
"Name \"{0}\" does not exist, please refresh",
"Nama \"{0}\" tidak ada, silakan refresh"
],
"名稱「{0}」已經刪掉了，這一段不能復原": [
"Name \"{0}\" has been deleted, this segment cannot be restored",
"Nama \"{0}\" sudah dihapus, segmen ini tidak bisa dikembalikan"
],
"否": [
"No",
"Tidak"
],
"啟動失敗": [
"Start failed",
"Gagal mulai"
],
"啟動監控": [
"Start monitoring",
"Mulai pantau"
],
"啟用": [
"Enable",
"Aktifkan"
],
"啟用（回到清單）": [
"Enable (back to the list)",
"Aktifkan (kembali ke daftar)"
],
"圓圈數字＝步驟順序，照影片裡第一次出現的先後": [
"Circled numbers = step order, by first appearance in the video",
"Angka dalam lingkaran = urutan langkah, sesuai urutan pertama muncul di video"
],
"在哪裡訓練": [
"Where to train",
"Tempat latih"
],
"在哪裡訓練：": [
"Where to train:",
"Tempat latih:"
],
"在目前時間新增一段（1 秒），再拉方塊右邊到結束的地方": [
"Add a segment (1 s) at the current time, then drag the block's right edge to where it ends",
"Tambah segmen (1 detik) di waktu sekarang, lalu tarik sisi kanan blok ke titik akhirnya"
],
"在這台訓練（CPU 約 100 分鐘）": [
"Train on this PC (CPU, about 100 min)",
"Latih di PC ini (CPU, sekitar 100 menit)"
],
"地區": [
"Region",
"Wilayah"
],
"地區 *": [
"Region *",
"Wilayah *"
],
"型體": [
"Style",
"Artikel"
],
"型體 *": [
"Style *",
"Artikel *"
],
"型體 {0}／{1} 已經有包裝方式了（{2}）": [
"Style {0}/{1} already has a packing method ({2})",
"Artikel {0}/{1} sudah punya metode kemas ({2})"
],
"型體 {0}／{1} 已經有包裝方式了（{2}）；要改它請到「包裝方式設定」": [
"Style {0}/{1} already has a packing method ({2}); to change it, go to \"Packing method settings\"",
"Artikel {0}/{1} sudah punya metode kemas ({2}); untuk mengubahnya buka \"Pengaturan metode kemas\""
],
"型體 {0}／{1} 已經有包裝方式了（{2}）；要改它請到「包裝明細」": [
"Style {0}/{1} already has a packing method ({2}); to change it, go to \"Packing details\"",
"Artikel {0}/{1} sudah punya metode kemas ({2}); untuk mengubahnya buka \"Rincian kemas\""
],
"型體名稱": [
"Style name",
"Nama artikel"
],
"型體和地區都要填": [
"Both Style and Region are required",
"Artikel dan Wilayah wajib diisi"
],
"型體地區": [
"Style/Region",
"Artikel/Wilayah"
],
"型體要照規定：6 碼數字＋空一格＋2 碼數字，例如 310222 01": [
"Style must be 6 digits + a space + 2 digits, e.g. 310222 01",
"Artikel harus 6 angka + spasi + 2 angka, contoh 310222 01"
],
"型體（代碼或名稱）": [
"Style (code or name)",
"Artikel (kode atau nama)"
],
"型體（代碼／名稱）": [
"Style (code/name)",
"Artikel (kode/nama)"
],
"外接蜂鳴器的指令還沒設定：請在 {0} 填 on_cmd／off_cmd": [
"External buzzer commands are not set: fill in on_cmd / off_cmd in {0}",
"Perintah buzzer eksternal belum diatur: isi on_cmd / off_cmd di {0}"
],
"外接蜂鳴器／警示燈": [
"External buzzer / warning light",
"Buzzer eksternal / lampu peringatan"
],
"大小": [
"Size",
"Ukuran"
],
"大約在 {0}～{1} 秒。點一下開標記頁補框（另開分頁）": [
"Around {0}–{1} s. Click to open the label page and add boxes (new tab)",
"Sekitar {0}–{1} detik. Klik untuk buka halaman tandai dan tambah kotak (tab baru)"
],
"失敗": [
"Failed",
"Gagal"
],
"失敗（{0}），10 分鐘內再試{1}": [
"Failed ({0}), retry within 10 min{1}",
"Gagal ({0}), coba lagi dalam 10 menit{1}"
],
"失敗：": [
"Failed: ",
"Gagal: "
],
"套用": [
"Apply",
"Terapkan"
],
"套用選取的候選": [
"Apply selected candidates",
"Terapkan kandidat terpilih"
],
"存截圖": [
"Save screenshot",
"Simpan screenshot"
],
"存截圖失敗": [
"Save screenshot failed",
"Gagal simpan screenshot"
],
"存檔失敗": [
"Save failed",
"Gagal menyimpan"
],
"它追出來的框也會一起刪。": [
"The boxes it tracked will be deleted too.",
"Kotak hasil pelacakannya juga ikut terhapus."
],
"完成": [
"Done",
"Selesai"
],
"完成 : 錯誤": [
"Done : Error",
"Selesai : Salah"
],
"完成 {0} 輪・漏做 {1} 輪": [
"{0} cycles done · {1} missed",
"{0} siklus selesai · {1} terlewat"
],
"客戶": [
"Customer",
"Customer"
],
"專案": [
"Project",
"Proyek"
],
"專案「{0}」不存在": [
"Project \"{0}\" does not exist",
"Proyek \"{0}\" tidak ada"
],
"專案「{0}」已存在": [
"Project \"{0}\" already exists",
"Proyek \"{0}\" sudah ada"
],
"專案名稱不可包含這些字元：": [
"Project name cannot contain these characters: ",
"Nama proyek tidak boleh berisi karakter ini: "
],
"專案名稱長度必須是 1～50 個字元": [
"Project name must be 1–50 characters",
"Nama proyek harus 1–50 karakter"
],
"專案名稱頭尾不可是空白或句點": [
"Project name cannot start or end with a space or period",
"Nama proyek tidak boleh diawali atau diakhiri spasi atau titik"
],
"專案有 gesture_anchors，需要 YOLO-World 權重": [
"Project has gesture_anchors, YOLO-World weights required",
"Proyek punya gesture_anchors, perlu bobot YOLO-World"
],
"專案沒有任何步驟": [
"Project has no steps",
"Proyek tidak punya langkah"
],
"專案資料夾路徑或 sop_projects 下的專案名稱": [
"Project folder path or project name under sop_projects",
"Path folder proyek atau nama proyek di sop_projects"
],
"專案資料夾（不能改）": [
"Project folder (cannot change)",
"Folder proyek (tidak bisa diubah)"
],
"專案（包裝方式）": [
"Project (Packing method)",
"Proyek (Metode kemas)"
],
"對得上：模型認得「{0}」，手碰到它": [
"Match: model recognizes \"{0}\" and the hand touches it",
"Cocok: model mengenali \"{0}\" dan tangan menyentuhnya"
],
"尚未啟動": [
"Not started",
"Belum mulai"
],
"差不多": [
"About the same",
"Hampir sama"
],
"已上傳 {0}": [
"Uploaded {0}",
"Sudah upload {0}"
],
"已上傳「{0}」成 {1}，並設成目前版本": [
"Uploaded \"{0}\" as {1} and set it as current version",
"\"{0}\" sudah diunggah sebagai {1} dan dijadikan versi aktif"
],
"已停止": [
"Stopped",
"Berhenti"
],
"已停用「{0}」：收到「操作 → 停用的包裝方式」，可以在那裡啟用或刪除": [
"Disabled \"{0}\": moved to \"Actions → Disabled packing methods\", where you can enable or delete it",
"\"{0}\" dinonaktifkan: dipindah ke \"Aksi → Metode kemas nonaktif\", di sana bisa diaktifkan atau dihapus"
],
"已儲存": [
"Saved",
"Tersimpan"
],
"已儲存：{0} 第 {1} 段。系統判斷這個動作是手碰到「{2}」（{3}／{4} 格有手時手在它上面），監控時用它的框來判斷。": [
"Saved: {0} segment {1}. The system decided this action is the hand touching \"{2}\" (hand was on it in {3}/{4} frames with a hand), and uses its box when monitoring.",
"Tersimpan: {0} segmen {1}. Sistem menilai gerakan ini adalah tangan menyentuh \"{2}\" (tangan ada di atasnya pada {3}/{4} frame yang ada tangan), dan memakai kotaknya saat pantau."
],
"已儲存：{0} 第 {1} 段，追到 {2}／{3} 格會拿去訓練。": [
"Saved: {0} segment {1}. {2}/{3} frames tracked will be used for training.",
"Tersimpan: {0} segmen {1}. {2}/{3} frame yang terlacak akan dipakai untuk latih."
],
"已切到 {0}": [
"Switched to {0}",
"Pindah ke {0}"
],
"已刪除 {0} 個包裝方式": [
"Deleted {0} packing method(s)",
"{0} metode kemas dihapus"
],
"已刪除 {0} 格錯框": [
"Deleted {0} wrong box frames",
"Sudah hapus {0} frame kotak salah"
],
"已刪除名稱「{0}」": [
"Deleted name \"{0}\"",
"Nama \"{0}\" sudah dihapus"
],
"已刪除第 {0} 段（Ctrl＋Z 可以復原）": [
"Deleted segment {0} (Ctrl＋Z to undo)",
"Segmen {0} sudah dihapus (Ctrl＋Z untuk batalkan)"
],
"已加入時間軸：": [
"Added to the timeline: ",
"Ditambahkan ke linimasa: "
],
"已匯入 {0}（{1}x{2} @ {3} fps）": [
"Imported {0} ({1}x{2} @ {3} fps)",
"Sudah diimpor {0} ({1}x{2} @ {3} fps)"
],
"已匯入，開始離線驗證（保留段 {0} 段）": [
"Imported, starting offline verification ({0} held-out segments)",
"Sudah diimpor, mulai verifikasi offline ({0} segmen cadangan)"
],
"已取消": [
"Cancelled",
"Dibatalkan"
],
"已啟用「{0}」": [
"Enabled \"{0}\"",
"\"{0}\" diaktifkan"
],
"已啟用：這個網頁會出聲。": [
"Enabled: this page will make sound.",
"Aktif: halaman ini akan berbunyi."
],
"已存 物品 {0} 段・動作 {1} 段": [
"Saved: items {0} segments・actions {1} segments",
"Tersimpan: barang {0} segmen・gerakan {1} segmen"
],
"已存 物品 {0} 段・動作 {1} 段・舊版 {2} 格": [
"Saved: items {0} segments・actions {1} segments・old boxes {2} frames",
"Tersimpan: barang {0} segmen・gerakan {1} segmen・kotak lama {2} frame"
],
"已存 空桌面 {0} 格・物品 {1} 段・動作 {2} 段": [
"Saved: empty desk {0} frame(s), items {1} segment(s), actions {2} segment(s)",
"Tersimpan: meja kosong {0} bingkai, barang {1} segmen, gerakan {2} segmen"
],
"已存成 {0}。但共用硬碟目前是 {1}，是你載入之後別人傳的。要把你的 {2} 設成目前版本嗎？選「先不要」就只存著，大家還是載入 {3}。": [
"Saved as {0}. But the shared drive's current version is {1}, uploaded by someone else after you loaded. Set your {2} as the current version? Choose \"Not now\" to only keep it saved; everyone will still load {3}.",
"Tersimpan sebagai {0}. Tapi versi aktif di drive bersama adalah {1}, diunggah orang lain setelah Anda memuat. Jadikan {2} Anda sebagai versi aktif? Pilih \"Nanti dulu\" untuk hanya menyimpan; semua orang tetap memuat {3}."
],
"已存截圖：": [
"Screenshot saved: ",
"Screenshot disimpan: "
],
"已存：": [
"Saved: ",
"Tersimpan: "
],
"已復原上一步": [
"Undid last step",
"Langkah terakhir dibatalkan"
],
"已復原到 {0}": [
"Restored to {0}",
"Dikembalikan ke {0}"
],
"已排入分析，前面的跑完就會開始": [
"Queued for analysis, will start when earlier jobs finish",
"Masuk antrean analisis, mulai setelah yang sebelumnya selesai"
],
"已換上": [
"In use",
"Sudah dipakai"
],
"已換上（自己選的）": [
"In use (your choice)",
"Sudah dipakai (pilihan sendiri)"
],
"已新增「{0}」。移到它出現的地方，按「從這裡開始」": [
"Added \"{0}\". Move to where it appears and click \"Start here\"",
"\"{0}\" ditambahkan. Pindah ke tempat ia muncul, klik \"Mulai dari sini\""
],
"已新增動作「{0}」。移到動作開始的地方，按「從這裡開始」，拉範圍就好，不用畫框": [
"Added action \"{0}\". Move to where the action starts, click \"Start here\" and drag the range. No box needed",
"Gerakan \"{0}\" ditambahkan. Pindah ke awal gerakan, klik \"Mulai dari sini\", lalu tarik rentangnya. Tidak perlu gambar kotak"
],
"已更新配色「": [
"Updated color \"",
"Warna diperbarui \""
],
"已標 {0} 格空桌面": [
"{0} empty-desk frame(s) marked",
"{0} bingkai meja kosong ditandai"
],
"已標 {0} 格空桌面；標好按右下「下一步」": [
"{0} empty-desk frame(s) marked; when done, press \"Next\" at the bottom right",
"{0} bingkai meja kosong ditandai; kalau sudah, tekan \"Berikutnya\" di kanan bawah"
],
"已照你的選擇換上新模型（比上次差）": [
"Switched to the new model as you chose (worse than last time)",
"Sudah ganti ke model baru sesuai pilihan Anda (lebih jelek dari sebelumnya)"
],
"已經 {0} 秒沒看到手（作業員不在，或鏡頭被擋住）": [
"No hand seen for {0} s (worker away, or camera blocked)",
"Sudah {0} detik tidak terlihat tangan (operator tidak ada, atau kamera terhalang)"
],
"已經在找候選步驟，請等它跑完": [
"Already finding candidate steps, please wait for it to finish",
"Sedang mencari kandidat langkah, tunggu sampai selesai"
],
"已經在訓練中，請等它跑完": [
"Training already running, please wait until it finishes",
"Sedang latih, tunggu sampai selesai"
],
"已經有「{0}」了，直接點它就好": [
"\"{0}\" already exists, just click it",
"\"{0}\" sudah ada, langsung klik saja"
],
"已記住共用硬碟資料夾": [
"Shared drive folder saved",
"Folder drive bersama sudah diingat"
],
"已載入「{0}」{1}{2}。到監控畫面「操作 → 換包裝方式」就能選": [
"Loaded \"{0}\"{1}{2}. Select it in Monitor screen \"Actions → Change packing method\"",
"\"{0}\"{1}{2} sudah dimuat. Pilih di Layar pantau \"Aksi → Ganti metode kemas\""
],
"已選 {0} 個候選 → {1} 個步驟": [
"{0} candidates selected → {1} steps",
"{0} kandidat dipilih → {1} langkah"
],
"已選 {0} 段（訓練 {1}、驗證 {2}），共 {3} 框；配色：{4}": [
"{0} segments selected (train {1}, verify {2}), {3} boxes total; colors: {4}",
"{0} segmen dipilih (latih {1}, verifikasi {2}), total {3} kotak; warna: {4}"
],
"已開始上傳": [
"Upload started",
"Upload dimulai"
],
"已驗證": [
"Verified",
"Terverifikasi"
],
"已驗證 {0} / {1} 個配色": [
"Verified {0} / {1} colors",
"Terverifikasi {0} / {1} warna"
],
"平均完成時間": [
"Average completion time",
"Rata-rata waktu selesai"
],
"平常不用：程式會用全部框過的物品自動算。只有要特別放大或縮小看的範圍才自己框": [
"Usually not needed: the program calculates it from all boxed items. Draw it yourself only if you need a larger or smaller area",
"Biasanya tidak perlu: program menghitung otomatis dari semua barang yang sudah diberi kotak. Gambar sendiri hanya jika perlu area lebih besar atau kecil"
],
"廠別": [
"Factory",
"Pabrik"
],
"廠別只能選": [
"Factory can only be ",
"Pabrik hanya boleh "
],
"延伸不出任何訓練圖": [
"Could not extend to any training images",
"Tidak bisa memperluas ke gambar latih mana pun"
],
"延伸框選{0}：{1}/{2}": [
"Extending boxes{0}: {1}/{2}",
"Memperluas kotak{0}: {1}/{2}"
],
"延伸框選：{0}/{1}": [
"Extending boxes: {0}/{1}",
"Memperluas kotak: {0}/{1}"
],
"建立": [
"Create",
"Buat"
],
"建立步驟庫（{0}）：{1}/{2} 格": [
"Building step library ({0}): {1}/{2} frames",
"Membangun pustaka langkah ({0}): {1}/{2} bingkai"
],
"影像來源": [
"Video source",
"Sumber video"
],
"影像編碼失敗：{0}": [
"Video encoding failed: {0}",
"Encode video gagal: {0}"
],
"影片": [
"Video",
"Video"
],
"影片 {0}×{1}，{2}，{3} fps": [
"Video {0}×{1}, {2}, {3} fps",
"Video {0}×{1}, {2}, {3} fps"
],
"影片檔來源 + --show 時不照原速播放（預設照 fps 放慢）": [
"For video file source + --show: don't play at original speed (default slows to fps)",
"Untuk sumber file video + --show: tidak diputar dengan kecepatan asli (default diperlambat sesuai fps)"
],
"影片結束前沒做完": [
"Not finished before the video ended",
"Belum selesai sampai video habis"
],
"影片讀不到任何影格：{0}": [
"Cannot read any frames from video: {0}",
"Tidak ada frame yang terbaca dari video: {0}"
],
"影片配色": [
"Video color",
"Warna video"
],
"往前 1 格": [
"Back 1 frame",
"Mundur 1 frame"
],
"往前 1 格（←）": [
"Back 1 frame (←)",
"Mundur 1 frame (←)"
],
"往前 1 秒": [
"Back 1 s",
"Mundur 1 detik"
],
"往前 1 秒（Shift＋←、J）": [
"Back 1 s (Shift＋←, J)",
"Mundur 1 detik (Shift＋←, J)"
],
"往後 1 格": [
"Forward 1 frame",
"Maju 1 frame"
],
"往後 1 格（→）": [
"Forward 1 frame (→)",
"Maju 1 frame (→)"
],
"往後 1 秒": [
"Forward 1 s",
"Maju 1 detik"
],
"往後 1 秒（Shift＋→、L 播放）": [
"Forward 1 s (Shift＋→, L to play)",
"Maju 1 detik (Shift＋→, L untuk putar)"
],
"從共用硬碟更新": [
"Update from shared drive",
"Perbarui dari drive bersama"
],
"從清單移除": [
"Remove from list",
"Hapus dari daftar"
],
"從這裡開始": [
"Start here",
"Mulai dari sini"
],
"復原": [
"Undo",
"Kembalikan"
],
"復原（取消待刪）": [
"Undo (cancel pending delete)",
"Batalkan (batal hapus)"
],
"必要": [
"Required",
"Wajib"
],
"必要 {0} / {1}": [
"Required {0} / {1}",
"Wajib {0} / {1}"
],
"必要 {0} 步": [
"{0} required steps",
"{0} langkah wajib"
],
"必要步驟 {0}/{1}": [
"Required steps {0}/{1}",
"Langkah wajib {0}/{1}"
],
"怎麼判": [
"How it's judged",
"Cara menilai"
],
"怎麼判好壞": [
"How better/worse is decided",
"Cara menilai lebih baik/buruk"
],
"成型": [
"Assembly",
"Assembly"
],
"或手在重置區停一下": [
"or hold your hand in the reset zone for a moment",
"atau tahan tangan sebentar di area reset"
],
"手勢模型「{0}」是特徵版本 {1}，目前程式是版本 {2}，請到「② 分段說明動作」重新按「訓練並產生步驟」": [
"Gesture model \"{0}\" uses feature version {1}, but the program is version {2}. Go to \"② Describe actions by segment\" and press \"Train and generate steps\" again",
"Model gerakan tangan \"{0}\" memakai versi fitur {1}, program sekarang versi {2}. Buka \"② Jelaskan gerakan per segmen\" lalu tekan lagi \"Latih dan buat langkah\""
],
"手勢：{0} {1}": [
"Gesture: {0} {1}",
"Gestur: {0} {1}"
],
"手在盒內，暫不判定": [
"Hand in box, not judging yet",
"Tangan di dalam kotak, belum dinilai"
],
"手框": [
"Manual",
"Manual"
],
"手框 {0}、自動 {1}": [
"Manual {0}, auto {1}",
"Manual {0}, otomatis {1}"
],
"手沒有落在任何已框的物品上（這幾秒有框的是：{0}）。先把被手碰到的東西框好再存。": [
"The hand is not on any boxed item (boxed in these seconds: {0}). Box the thing the hand touches first, then save.",
"Tangan tidak berada di barang yang sudah dikotak (yang dikotak di detik ini: {0}). Kotak dulu barang yang disentuh tangan, lalu simpan."
],
"手碰到「{0}」的格數不夠（{1}／{2} 格有手，": [
"Not enough frames with the hand touching \"{0}\" ({1}/{2} frames have a hand, ",
"Frame tangan menyentuh \"{0}\" kurang ({1}/{2} frame ada tangan, "
],
"手碰：{0}": [
"Hand touch: {0}",
"Sentuhan tangan: {0}"
],
"手移動很快": [
"Hands move fast",
"Tangan bergerak cepat"
],
"手要碰的是小地方（例如鞋舌）：先把它框成物品": [
"If the hand touches a small spot (e.g. tongue): box it as an item first",
"Kalau tangan menyentuh bagian kecil (contoh: lidah sepatu): beri kotak sebagai barang dulu"
],
"手部步驟要指定物件（英文提示或已框的物品）": [
"Hand steps need an object (English prompt or a boxed item)",
"Langkah tangan harus punya objek (prompt bahasa Inggris atau barang yang sudah dikotak)"
],
"打包 GPU 訓練包中…": [
"Packing GPU training package…",
"Mengemas paket latih GPU…"
],
"找一格桌上沒東西的畫面，按「這一格標成空桌面」": [
"Find a frame with nothing on the desk and press \"Mark this frame as empty desk\"",
"Cari bingkai yang mejanya kosong, lalu tekan \"Tandai bingkai ini sebagai meja kosong\""
],
"找不到 paplay／aplay，裝 pulseaudio-utils 或 alsa-utils": [
"paplay/aplay not found; install pulseaudio-utils or alsa-utils",
"paplay/aplay tidak ditemukan; pasang pulseaudio-utils atau alsa-utils"
],
"找不到 {0}，無法找盒子": [
"Cannot find {0}, cannot find boxes",
"{0} tidak ditemukan, tidak bisa mencari kotak"
],
"找不到「{0}」": [
"\"{0}\" not found",
"\"{0}\" tidak ditemukan"
],
"找不到參考來源「{0}」": [
"Reference source \"{0}\" not found",
"Sumber referensi \"{0}\" tidak ditemukan"
],
"找不到影片檔：{0}": [
"Video file not found: {0}",
"File video tidak ditemukan: {0}"
],
"找不到影片：{0}": [
"Video not found: {0}",
"Video tidak ditemukan: {0}"
],
"找不到手勢模型：{0}": [
"Gesture model not found: {0}",
"Model gesture tidak ditemukan: {0}"
],
"找不到手部模型 {0}，無法判斷這個動作碰到什麼": [
"Hand model {0} not found, cannot tell what this action touches",
"Model tangan {0} tidak ditemukan, tidak bisa tahu gerakan ini menyentuh apa"
],
"找不到手部模型檔：{0}（請依 models/README.md 下載）": [
"Hand model file not found: {0} (download per models/README.md)",
"File model tangan tidak ditemukan: {0} (unduh sesuai models/README.md)"
],
"找不到物件偵測權重：{0}": [
"Object detection weights not found: {0}",
"Bobot deteksi objek tidak ditemukan: {0}"
],
"找不到產線「{0}」": [
"Line \"{0}\" not found",
"Lini \"{0}\" tidak ditemukan"
],
"找不到示範影片": [
"Demo video not found",
"Video contoh tidak ditemukan"
],
"找不到示範影片：{0}": [
"Demo video not found: {0}",
"Video contoh tidak ditemukan: {0}"
],
"找不到設定檔：{0}": [
"Settings file not found: {0}",
"File pengaturan tidak ditemukan: {0}"
],
"找不到這個包裝方式的 GPU 訓練計畫（candidate_plan.json），請先在這台產生 GPU 訓練包": [
"No GPU training plan found for this packing method (candidate_plan.json). Create a GPU training package on this PC first",
"Rencana latih GPU untuk metode kemas ini tidak ditemukan (candidate_plan.json). Buat paket latih GPU di PC ini dulu"
],
"找不到頁面": [
"Page not found",
"Halaman tidak ditemukan"
],
"找其他輪": [
"Finding other cycles",
"Mencari siklus lain"
],
"找到 {0} 個候選步驟": [
"Found {0} candidate steps",
"Ditemukan {0} kandidat langkah"
],
"找到率": [
"Find rate",
"Tingkat temuan"
],
"找到率（上次 → 這次）": [
"Find rate (last → this)",
"Tingkat temuan (sebelum → sekarang)"
],
"找手的位置：{0}/{1} 格": [
"Locating hands: {0}/{1} frames",
"Mencari posisi tangan: {0}/{1} bingkai"
],
"找桌上什麼都沒有的畫面標起來（建議 2～3 格），模型才學得到「桌上沒東西」": [
"Mark frames where the desk is completely empty (2–3 recommended) so the model learns what \"nothing on the desk\" looks like",
"Tandai bingkai yang mejanya benar-benar kosong (disarankan 2–3) supaya model belajar \"meja kosong\""
],
"找桌上什麼都沒有的畫面（盒子、鞋子都還沒放上來），按下方「這一格標成空桌面」。建議在不同時間標 2～3 格，模型比較不會把空桌面認成物品。": [
"Find a frame where the desk is completely empty (no box or shoes yet) and press \"Mark this frame as empty desk\" below. Mark 2–3 frames at different times so the model is less likely to mistake an empty desk for an item.",
"Cari bingkai yang mejanya benar-benar kosong (belum ada kotak atau sepatu), lalu tekan \"Tandai bingkai ini sebagai meja kosong\" di bawah. Tandai 2–3 bingkai di waktu berbeda supaya model tidak salah mengira meja kosong sebagai barang."
],
"找盒子與手{0}：{1}/{2} 格": [
"Finding boxes and hands{0}: {1}/{2} frames",
"Mencari kotak dan tangan{0}: {1}/{2} frame"
],
"找盒子與手：{0}/{1} 格": [
"Finding boxes and hands: {0}/{1} frames",
"Mencari kotak dan tangan: {0}/{1} frame"
],
"把 {0} 設成目前版本（大家之後載入這一版）": [
"Set {0} as current version (everyone will load this version)",
"Jadikan {0} versi aktif (semua orang akan memuat versi ini)"
],
"把事件與截圖寫進專案的 error_logs/": [
"Write events and screenshots to the project's error_logs/",
"Tulis kejadian dan tangkapan layar ke error_logs/ proyek"
],
"把框裡沒顏色的部分（黑／白／灰鞋）換成白、灰、紅、深藍、咖啡、米色，每張多做 2 份，讓模型不要只認一種顏色。要換的物品：": [
"Recolor the colorless parts inside the box (black/white/gray shoes) to white, gray, red, navy, brown and beige, 2 extra copies per image, so the model doesn't learn only one color. Items to recolor: ",
"Ganti warna bagian tanpa warna di dalam kotak (sepatu hitam/putih/abu) jadi putih, abu, merah, biru tua, cokelat, krem, tambah 2 salinan per gambar, supaya model tidak hanya kenal satu warna. Barang yang diganti warnanya: "
],
"抽特徵": [
"Extracting features",
"Mengambil fitur"
],
"拉好範圍，按「儲存這一段」": [
"Drag the range, then click \"Save this segment\"",
"Tarik rentangnya, lalu klik \"Simpan segmen ini\""
],
"拉方塊右邊到動作結束的地方，按「儲存這一段」就好，不用畫框。": [
"Drag the block's right edge to where the action ends and click \"Save this segment\". No box needed.",
"Tarik sisi kanan blok ke akhir gerakan, lalu klik \"Simpan segmen ini\". Tidak perlu gambar kotak."
],
"拖拉框住整個桌面；Esc 取消": [
"Drag a box around the whole desk; Esc to cancel",
"Tarik kotak di seluruh meja; Esc untuk batal"
],
"拖拉調整欄寬（雙擊恢復預設）": [
"Drag to resize column (double-click to reset)",
"Seret untuk ubah lebar kolom (klik dua kali untuk reset)"
],
"按 Ctrl+C 結束": [
"Press Ctrl+C to exit",
"Tekan Ctrl+C untuk keluar"
],
"按「儲存這一段」": [
"Click \"Save this segment\"",
"Klik \"Simpan segmen ini\""
],
"按「前往監控」，到監控畫面換線、啟動": [
"Click \"Go to Monitor\" to switch line and start on the Monitor screen",
"Klik \"Ke Pantau\", lalu ganti lini dan mulai di Layar pantau"
],
"按「從這裡開始」": [
"Click \"Start here\"",
"Klik \"Mulai dari sini\""
],
"按「解除警告」": [
"Press \"Clear warning\"",
"Tekan \"Hapus peringatan\""
],
"按右下角的設定鍵設定這台電腦的產線": [
"Press the settings button at bottom right to set this PC's line",
"Tekan tombol pengaturan di kanan bawah untuk atur lini PC ini"
],
"挑片段、合成配色、產生 GPU 訓練包、匯入 GPU 模型": [
"Pick clips, synthesize colorways, build GPU training pack, import GPU model",
"Pilih klip, buat variasi warna, buat paket latih GPU, impor model GPU"
],
"接 EIP 要先填廠別": [
"Enter the Factory before connecting to EIP",
"Isi Pabrik dulu sebelum sambung ke EIP"
],
"換上": [
"Use it",
"Pakai"
],
"換上失敗": [
"Failed to switch",
"Gagal ganti"
],
"換包裝方式": [
"Change packing method",
"Ganti metode kemas"
],
"換線": [
" Change line",
" Ganti lini"
],
"換線失敗": [
"Line change failed",
"Gagal ganti lini"
],
"播放": [
"Play",
"Putar"
],
"播放程式結束碼 {0}": [
"Player exit code {0}",
"Kode keluar pemutar {0}"
],
"播放／暫停（空白鍵）": [
"Play/Pause (Space)",
"Putar/Jeda (Spasi)"
],
"操作": [
"Actions",
"Aksi"
],
"收起／展開側欄": [
"Collapse / expand sidebar",
"Tutup / buka panel samping"
],
"收起／展開側欄（掛在產線旁的螢幕可以收起來）": [
"Collapse / expand sidebar (can be collapsed on screens beside the line)",
"Tutup / buka panel samping (layar di samping lini bisa ditutup)"
],
"放大 {0} 倍・右鍵拖拉移動": [
"Zoom {0}x・right-drag to move",
"Zoom {0}x・tarik klik kanan untuk geser"
],
"放大時間軸": [
"Zoom in timeline",
"Perbesar timeline"
],
"整支影片，拖拉框框換位置": [
"Whole video, drag the box to move it",
"Seluruh video, tarik kotak untuk pindah posisi"
],
"新動作，例如 檢查鞋舌": [
"New action, e.g. Check tongue",
"Gerakan baru, contoh: Cek lidah sepatu"
],
"新包裝方式": [
"New packing method",
"Metode kemas baru"
],
"新名稱": [
"New name",
"Nama baru"
],
"新增": [
"Add",
"Tambah"
],
"新增包裝方式": [
"Add packing method",
"Tambah metode kemas"
],
"新增包裝方式 ›": [
"Add packing method ›",
"Tambah metode kemas ›"
],
"新增配色": [
"Add color",
"Tambah warna"
],
"新模型比上次差，還在用上次的模型（新模型存成 candidate.pt）": [
"New model is worse than last time, still using the previous model (new model saved as candidate.pt)",
"Model baru lebih jelek dari sebelumnya, masih pakai model lama (model baru disimpan sebagai candidate.pt)"
],
"新物品": [
"New item",
"Barang baru"
],
"新配色": [
"New colorway",
"Warna baru"
],
"新配色（模型沒看過）": [
"New color (model has not seen it)",
"Warna baru (model belum pernah lihat)"
],
"是": [
"Yes",
"Ya"
],
"時間": [
"Time",
"Waktu"
],
"時間格式看不懂。可以打 12.4、0:12.4 或 00:12.4。": [
"Time format not recognized. You can type 12.4, 0:12.4 or 00:12.4.",
"Format waktu tidak dikenali. Bisa ketik 12.4, 0:12.4 atau 00:12.4."
],
"時間軸現在只顯示「{0}」。": [
"The timeline now shows only \"{0}\".",
"Timeline sekarang hanya menampilkan \"{0}\"."
],
"時間軸縮放": [
"Timeline zoom",
"Zoom timeline"
],
"時間（秒）": [
"Time (s)",
"Waktu (detik)"
],
"暫停": [
"Pause",
"Jeda"
],
"最多叫": [
"Sound for at most",
"Bunyi paling lama"
],
"最多處理幾格，0 = 全部": [
"Max frames to process, 0 = all",
"Maksimal frame diproses, 0 = semua"
],
"最快 {0} 秒、最慢 {1} 秒、上一輪 {2} 秒": [
"Fastest {0} s, slowest {1} s, last cycle {2} s",
"Tercepat {0} detik, terlama {1} detik, siklus terakhir {2} detik"
],
"最近幾次訓練": [
"Recent trainings",
"Pelatihan terakhir"
],
"最近輪次": [
"Recent cycles",
"Siklus terakhir"
],
"有": [
"Yes",
"Ada"
],
"有 box_state／item 步驟時，要設定 state_anchor（錨點）或 state_fixed（固定區域）": [
"With box_state/item steps, set state_anchor (anchor) or state_fixed (fixed area)",
"Kalau ada langkah box_state/item, atur state_anchor (anchor) atau state_fixed (area tetap)"
],
"有一半以上沒追到：東西可能被遮住或轉向了，把這段切短、或在沒追到的地方再框一次並重新儲存。": [
"More than half was not tracked: the item may be covered or turned. Make this segment shorter, or box it again where tracking was lost and save again.",
"Lebih dari setengah tidak terlacak: barang mungkin tertutup atau berputar. Perpendek segmen ini, atau beri kotak lagi di bagian yang tidak terlacak lalu simpan ulang."
],
"有影片、還沒框選；按預覽可以先分析步驟、自動切出每一輪": [
"Has video, no boxes yet; click Preview to analyze steps first and auto-split each cycle",
"Ada video, belum ada kotak; klik Pratinjau untuk analisis langkah dulu dan otomatis potong tiap siklus"
],
"有沒有換上": [
"Switched?",
"Sudah diganti?"
],
"有要看手的步驟才標，沒有就跳過：先有被碰的物品，再拉動作的範圍、儲存": [
"Label only steps that need hand checking, otherwise skip: have the touched item first, then drag the action range and save",
"Tandai hanya langkah yang perlu cek tangan, kalau tidak ada lewati: siapkan barang yang disentuh dulu, lalu tarik rentang gerakan dan simpan"
],
"未存": [
"Not saved",
"Belum disimpan"
],
"未完成": [
"Not done",
"Belum selesai"
],
"未指定": [
"Not set",
"Belum ditentukan"
],
"未框": [
"No box",
"Belum ada kotak"
],
"未驗證": [
"Not verified",
"Belum diverifikasi"
],
"本型體地區": [
"This style's regions",
"Wilayah artikel ini"
],
"本型體地區（{0}）": [
"This Style/Region ({0})",
"Artikel/Wilayah ini ({0})"
],
"本機": [
"Local",
"Lokal"
],
"本機 v{0}、共用硬碟目前 v{1}：操作 → 共用硬碟 → 載入": [
"Local v{0}, shared drive now v{1}: Actions → Shared drive → Load",
"Lokal v{0}, drive bersama sekarang v{1}: Aksi → Drive bersama → Muat"
],
"本機 {0}、目前版本 v{1}": [
"Local {0}, current version v{1}",
"Lokal {0}, versi sekarang v{1}"
],
"本機不是目前版本": [
"Local is not the current version",
"Versi lokal bukan versi aktif"
],
"本機改過，還沒上傳": [
"Changed locally, not uploaded yet",
"Diubah di lokal, belum diunggah"
],
"本機沒有": [
"Not on this computer",
"Tidak ada di lokal"
],
"本機版本": [
"Local version",
"Versi lokal"
],
"本站今日完成": [
"this station today",
"stasiun ini hari ini"
],
"本站今日完成：": [
"This station completed today: ",
"Selesai di stasiun ini hari ini: "
],
"本輪已結束，等待下一輪開始": [
"This cycle is done, waiting for next cycle",
"Siklus ini selesai, menunggu siklus berikutnya"
],
"本輪步驟": [
"Steps this cycle",
"Langkah siklus ini"
],
"本輪用時": [
"Time this cycle",
"Waktu siklus ini"
],
"本輪超時，尚未完成：": [
"Cycle overtime, not finished: ",
"Siklus lewat waktu, belum selesai: "
],
"查看": [
"View",
"Lihat"
],
"查看候選步驟": [
"View candidate steps",
"Lihat kandidat langkah"
],
"查詢": [
"Search",
"Cari"
],
"框「{0}」做完的樣子，連旁邊的盒子一起框": [
"Box how \"{0}\" looks when done, including the box next to it",
"Beri kotak bentuk \"{0}\" saat selesai, termasuk kotak di sebelahnya"
],
"框做完的樣子，連旁邊的盒子一起框": [
"Box how it looks when done, including the box next to it",
"Beri kotak bentuk saat selesai, termasuk kotak di sebelahnya"
],
"框做完的樣子，連旁邊的盒子一起框；先拉方塊右邊到物品離開畫面的地方，再在左邊畫面上框。": [
"Box how it looks when done, including the box next to it; first drag the block's right edge to where the item leaves the frame, then draw the box on the left view.",
"Beri kotak bentuk saat selesai, termasuk kotak di sebelahnya; tarik dulu sisi kanan blok ke titik barang keluar layar, lalu gambar kotak di layar kiri."
],
"框好了。按「儲存這一段」，這一段每一格都會自動追蹤這個框，拿去訓練。": [
"Box done. Click \"Save this segment\" and every frame in this segment will auto-track this box for training.",
"Kotak sudah dibuat. Klik \"Simpan segmen ini\", setiap frame di segmen ini akan otomatis melacak kotak ini untuk latih."
],
"框物品": [
"Box item",
"Beri kotak barang"
],
"框選段": [
"Boxed segments",
"Segmen berkotak"
],
"框選沒改也可以再訓練一次": [
"You can train again even if the boxes did not change",
"Boleh latih lagi walau kotak tidak berubah"
],
"框選的物品延伸不出任何一格；請確認「空盒／空桌面」有標、框選那一格看得到東西": [
"The boxed items could not be extended to any frame; check that \"empty box／empty desk\" is labeled and the item is visible in the boxed frame",
"Barang yang dikotak tidak bisa diperluas ke frame mana pun; pastikan \"kotak kosong／meja kosong\" sudah ditandai dan barangnya terlihat di frame yang dikotak"
],
"框（手／自動）": [
"Boxes (manual/auto)",
"Kotak (manual/otomatis)"
],
"桌上看到": [
"Seen on desk",
"Terlihat di meja"
],
"桌面": [
"Desk",
"Meja"
],
"桌面範圍": [
"Desk area",
"Area meja"
],
"桌面範圍改了，要重新訓練": [
"Desk area changed, please train again",
"Area meja berubah, perlu dilatih ulang"
],
"桌面範圍改回自動算（橘框），會跟著框選更新。": [
"Desk area set back to auto (orange box); it updates with the boxes.",
"Area meja kembali otomatis (kotak oranye), akan ikut berubah sesuai kotak barang."
],
"桌面範圍改成自己框的（橘框），之後不會自動改。": [
"Desk area set to your own box (orange box); it will not change automatically.",
"Area meja pakai kotak buatan sendiri (kotak oranye), tidak akan berubah otomatis."
],
"桌面範圍由程式用框過的物品自動算，不能自己框": [
"The desk area is calculated automatically from the boxed items and cannot be drawn by hand",
"Area meja dihitung otomatis dari barang yang sudah diberi kotak, tidak bisa digambar sendiri"
],
"桌面範圍裁切，每 0.5 秒一格。時間軸下方：綠色＝模型判定這一步完成的時間、紅色＝沒看到的步驟大約該在的位置（點一下跳過去）。": [
"Cropped to desk area, one frame every 0.5 s. Below the timeline: green = when the model judged this step done, red = where a missed step should roughly be (click to jump there).",
"Dipotong ke area meja, satu frame tiap 0,5 detik. Di bawah timeline: hijau = waktu model menilai langkah ini selesai, merah = perkiraan posisi langkah yang tidak terlihat (klik untuk lompat)."
],
"桌面範圍要是 [x, y, w, h]": [
"Desk area must be [x, y, w, h]",
"Area meja harus [x, y, w, h]"
],
"桌面範圍要是 [x, y, w, h] 四個數字，寬高大於 0": [
"Desk area must be [x, y, w, h], four numbers, width and height greater than 0",
"Area meja harus [x, y, w, h], empat angka, lebar dan tinggi lebih dari 0"
],
"桌面範圍（自動）": [
"Desk area (auto)",
"Area meja (otomatis)"
],
"桌面範圍（自己框的）": [
"Desk area (own box)",
"Area meja (kotak sendiri)"
],
"桌面範圍：改回自動算": [
"Desk area: back to auto",
"Area meja: kembali otomatis"
],
"桌面範圍：自己框（進階）": [
"Desk area: draw your own (advanced)",
"Area meja: gambar sendiri (lanjutan)"
],
"標好了。建議在別的時間再標 1～2 格": [
"Marked. It is best to mark 1–2 more at other times",
"Sudah ditandai. Sebaiknya tandai 1–2 lagi di waktu lain"
],
"標成已驗證": [
"Mark as verified",
"Tandai terverifikasi"
],
"標成待刪": [
"Mark for deletion",
"Tandai untuk dihapus"
],
"標成驗證判錯": [
"Mark as verify misjudged",
"Tandai verifikasi salah nilai"
],
"標記框": [
"Label boxes",
"Kotak tanda"
],
"標記框（{0}）": [
"Label boxes ({0})",
"Kotak tanda ({0})"
],
"標記物品": [
"Label items",
"Tandai barang"
],
"標記物品（框選、錄影、訓練）": [
"Label items (box, record, train)",
"Tandai barang (kotak, rekam, latih)"
],
"模型": [
"Model",
"Model"
],
"模型判成碰到「{0}」，存的時候是「{1}」。監控時會照「{2}」判，可能判不到；檢查這個動作的範圍或重存一次": [
"Model sees touching \"{0}\", but it was saved as \"{1}\". Monitor will judge by \"{2}\" and may not detect it; check this action's range or save it again",
"Model melihat sentuhan ke \"{0}\", tapi tersimpan sebagai \"{1}\". Saat pantau akan dinilai sebagai \"{2}\", mungkin tidak terdeteksi; cek rentang gerakan ini atau simpan ulang"
],
"模型在這個動作的時間裡認不到手碰的「{0}」（{1}／{2} 格）。": [
"During this action, the model cannot see the touched \"{0}\" ({1}/{2} frames).",
"Selama gerakan ini, model tidak mengenali \"{0}\" yang disentuh ({1}/{2} frame)."
],
"模型框": [
"Model boxes",
"Kotak model"
],
"模型要重新訓練。": [
"The model needs retraining.",
"Model perlu dilatih ulang."
],
"模型訓練": [
"Model training",
"Latih model"
],
"模型認得的物品": [
"Items the model recognizes",
"Barang yang dikenali model"
],
"模型追": [
"Model tracked",
"Dilacak model"
],
"模型（{0} 個地區，點哪個就切到哪個）": [
"Models ({0} regions, click one to switch to it)",
"Model ({0} wilayah, klik untuk pindah)"
],
"模型（點了就切換）": [
"Models (click to switch)",
"Model (klik untuk pindah)"
],
"檔案大小不合理（上限 2 GB）": [
"File size is not valid (max 2 GB)",
"Ukuran file tidak wajar (maks 2 GB)"
],
"檔案大小不合理（上限 500 MB）": [
"File size is not valid (max 500 MB)",
"Ukuran file tidak wajar (maks 500 MB)"
],
"正在上傳「{0}」…": [
"Uploading \"{0}\"…",
"Mengunggah \"{0}\"…"
],
"正在做": [
"In progress",
"Sedang dikerjakan"
],
"正在分析別的專案「{0}」，這個專案排在後面。": [
"Analyzing another project \"{0}\"; this project is queued after it.",
"Sedang analisis proyek lain \"{0}\", proyek ini antre setelahnya."
],
"正在分析步驟：{0}%（{1}/{2} 格，已 {3} 秒）。分析完會自動更新這個畫面。": [
"Analyzing steps: {0}% ({1}/{2} frames, {3} s elapsed). This screen updates automatically when done.",
"Sedang analisis langkah: {0}% ({1}/{2} frame, sudah {3} detik). Layar ini otomatis diperbarui setelah selesai."
],
"正在複製「{0}」{1}…": [
"Copying \"{0}\"{1}…",
"Menyalin \"{0}\"{1}…"
],
"正在訓練中，請等它跑完": [
"Training in progress, please wait until it finishes",
"Sedang latih, tunggu sampai selesai"
],
"正在訓練或驗證中，請等它跑完": [
"Training or validating, please wait until it finishes",
"Sedang latih atau verifikasi, tunggu sampai selesai"
],
"步": [
" steps",
" langkah"
],
"步驟": [
"Step",
"Langkah"
],
"步驟 {0}「{1}」是 hand_and_visual，但找不到樣板圖：{2}": [
"Step {0} \"{1}\" is hand_and_visual, but template image not found: {2}",
"Langkah {0} \"{1}\" pakai hand_and_visual, tapi gambar template tidak ditemukan: {2}"
],
"步驟 {0}「{1}」與步驟 {2}「{3}」的 ROI 重疊": [
"ROI of step {0} \"{1}\" overlaps step {2} \"{3}\"",
"ROI langkah {0} \"{1}\" tumpang tindih dengan langkah {2} \"{3}\""
],
"步驟分析 {0}：{1} 輪、完成 {2} 輪；沒看到的步驟 {3} 處（可能真的漏做，也可能模型沒認出來，請看畫面確認）。": [
"Step analysis {0}: {1} cycles, {2} completed; {3} unseen steps (may be truly missed, or the model didn't recognize them, please check the frames).",
"Analisis langkah {0}: {1} siklus, {2} selesai; {3} langkah tidak terlihat (bisa memang terlewat, bisa juga model tidak mengenali, cek gambarnya)."
],
"步驟分析失敗：": [
"Step analysis failed: ",
"Analisis langkah gagal: "
],
"步驟分析完成": [
"Step analysis done",
"Analisis langkah selesai"
],
"步驟名稱": [
"Step name",
"Nama langkah"
],
"步驟名稱不能重複": [
"Step names cannot repeat",
"Nama langkah tidak boleh sama"
],
"步驟名稱（如 翻鞋舌）": [
"Step name (e.g. flip tongue)",
"Nama langkah (mis. balik lidah sepatu)"
],
"步驟已完成": [
"Step done",
"Langkah selesai"
],
"步驟清單": [
"Step list",
"Daftar langkah"
],
"步驟超時：{0}": [
"Step overtime: {0}",
"Langkah lewat waktu: {0}"
],
"步驟都做完了，等這一輪結束": [
"　All steps done, waiting for this cycle to end",
"　Semua langkah selesai, tunggu siklus ini berakhir"
],
"步驟：": [
"Steps: ",
"Langkah: "
],
"段": [
" segments",
" segmen"
],
"每 150 格把預覽畫面存一張 jpg 到此資料夾（不開視窗也可用）": [
"Save a preview jpg to this folder every 150 frames (works without a window)",
"Simpan jpg pratinjau ke folder ini tiap 150 frame (bisa tanpa jendela)"
],
"每 60 秒把 FPS／記憶體／輪數寫一行到這個 csv（長時間測試用）": [
"Write a line of FPS / memory / cycles to this csv every 60 s (for long tests)",
"Tulis satu baris FPS / memori / siklus ke csv ini tiap 60 detik (untuk tes lama)"
],
"每個動作至少要標 {0} 段才會納入訓練，目前：{1}。": [
"Each action needs at least {0} labeled segments to be trained. Now: {1}.",
"Setiap gerakan perlu minimal {0} segmen ditandai agar ikut dilatih. Sekarang: {1}."
],
"每個物品比兩個數字。找到率：考卷裡有框的畫面，模型在同一個位置認出同一個物品的比例。空桌誤報：空桌畫面裡，模型說看到這個物品的比例。": [
"Each item is compared on two numbers. Find rate: in test frames with a box, how often the model recognizes the same item in the same place. Empty-desk false alarm: in empty-desk frames, how often the model says it sees this item.",
"Tiap barang dibandingkan dengan dua angka. Tingkat temuan: di frame tes yang ada kotaknya, seberapa sering model mengenali barang yang sama di posisi yang sama. Alarm palsu meja kosong: di frame meja kosong, seberapa sering model bilang melihat barang ini."
],
"每個物品的框都只有一段，出不了考題，沒有比較": [
"Each item's boxes are in only one segment, cannot make a test, no comparison",
"Kotak tiap barang hanya ada di satu segmen, tidak bisa buat tes, tidak ada perbandingan"
],
"每個配色會留「最後一段」不拿去訓練；訓練完用新模型掃那一段，標記過的物品都看到了才換上新模型，否則保留舊模型（新模型存成 candidate.pt）。某配色只勾一段就全部拿去訓練，這個配色這次無法驗證。配色欄可以直接改（整支影片同一個配色）。": [
"Each color keeps its \"last segment\" out of training; after training the new model scans that segment, and only if all labeled items are seen does it replace the old model, otherwise the old model is kept (new model saved as candidate.pt). If only one segment is checked for a color, all of it is used for training and that color can't be verified this time. The color column can be edited directly (one color per whole video).",
"Tiap warna menyisakan \"segmen terakhir\" yang tidak dipakai latih; setelah latih, model baru memindai segmen itu, dan baru menggantikan model lama kalau semua barang yang ditandai terlihat, kalau tidak model lama tetap dipakai (model baru disimpan sebagai candidate.pt). Kalau satu warna hanya dicentang satu segmen, semuanya dipakai latih dan warna itu tidak bisa diverifikasi kali ini. Kolom warna bisa langsung diubah (satu video satu warna)."
],
"每樣物品：從這裡開始 → 拉結尾 → 框做完的樣子（連旁邊的盒子）→ 儲存": [
"Each item: Start here → drag end → box how it looks when done (with the box next to it) → Save",
"Setiap barang: Mulai dari sini → tarik akhir → beri kotak bentuk saat selesai (dengan kotak di sebelahnya) → Simpan"
],
"每次長短不一": [
"Length varies a lot",
"Durasi sangat bervariasi"
],
"比上一次": [
"vs. last time",
"dibanding sebelumnya"
],
"比上次好，已換上新模型。上次的模型存成 best_prev_<時間>.pt。": [
"Better than last time; new model is now in use. Previous model saved as best_prev_<time>.pt.",
"Lebih baik dari sebelumnya; model baru sudah dipakai. Model sebelumnya disimpan sebagai best_prev_<waktu>.pt."
],
"比上次差，但已照你的選擇換上新模型。上次的模型存成 best_prev_<時間>.pt。": [
"Worse than last time, but the new model is in use as you chose. Previous model saved as best_prev_<time>.pt.",
"Lebih buruk dari sebelumnya, tapi model baru dipakai sesuai pilihan Anda. Model sebelumnya disimpan sebagai best_prev_<waktu>.pt."
],
"比上次差，還在用上次的模型。新模型存成 candidate.pt，沒有換上。": [
"Worse than last time; still using the previous model. New model saved as candidate.pt, not in use.",
"Lebih buruk dari sebelumnya; masih pakai model sebelumnya. Model baru disimpan sebagai candidate.pt, tidak dipakai."
],
"比較": [
"Compare",
"Bandingkan"
],
"沒接 EIP，只存本機": [
"No EIP connection, saved locally only",
"Tidak terhubung EIP, hanya disimpan di PC ini"
],
"沒換上": [
"Not switched",
"Tidak diganti"
],
"沒有": [
"None",
"Tidak ada"
],
"沒有「{0}」這個名稱": [
"No name \"{0}\"",
"Tidak ada nama \"{0}\""
],
"沒有「{0}」這個名稱，請先新增": [
"No name \"{0}\", please add it first",
"Tidak ada nama \"{0}\", tambahkan dulu"
],
"沒有上次可比": [
"Nothing previous to compare",
"Tidak ada hasil sebelumnya untuk dibandingkan"
],
"沒有候選 {0}": [
"No candidate {0}",
"Tidak ada kandidat {0}"
],
"沒有停用的包裝方式": [
"No disabled packing methods",
"Tidak ada metode kemas nonaktif"
],
"沒有可以復原的動作": [
"Nothing to undo",
"Tidak ada yang bisa dibatalkan"
],
"沒有可以復原的段落": [
"No segment to restore",
"Tidak ada segmen yang bisa dikembalikan"
],
"沒有可用的素材。先到「包裝設定（訓練）」錄影或上傳影片並框選。": [
"No usable material. First go to \"Packing setup (training)\" to record or upload video and draw boxes.",
"Tidak ada materi yang bisa dipakai. Ke \"Pengaturan kemas (latih)\" dulu untuk rekam atau unggah video lalu gambar kotak."
],
"沒有可用的素材。先到「標記物品」錄影或上傳影片並框選。": [
"No usable material. First go to \"Label items\" to record or upload video and draw boxes.",
"Tidak ada materi yang bisa dipakai. Ke \"Tandai barang\" dulu untuk rekam atau unggah video lalu gambar kotak."
],
"沒有已存的動作": [
"No saved actions",
"Belum ada gerakan tersimpan"
],
"沒有影片": [
"No video",
"Tidak ada video"
],
"沒有影片。": [
"No video.",
"Tidak ada video."
],
"沒有影片，不能分析。": [
"No video, cannot analyze.",
"Tidak ada video, tidak bisa analisis."
],
"沒有手的紀錄（trace.json）": [
"No hand record (trace.json)",
"Tidak ada catatan tangan (trace.json)"
],
"沒有收到檔案": [
"No file received",
"Tidak ada file yang diterima"
],
"沒有狀態範例": [
"No state examples",
"Tidak ada contoh status"
],
"沒有盒子": [
"No box",
"Tidak ada kotak"
],
"沒有空桌考題（空桌畫面少於 2 格），誤報不比。": [
"No empty-desk test (fewer than 2 empty-desk frames); false alarms not compared.",
"Tidak ada tes meja kosong (frame meja kosong kurang dari 2); alarm palsu tidak dibandingkan."
],
"沒有符合條件的包裝方式": [
"No matching packing methods",
"Tidak ada metode kemas yang cocok"
],
"沒有符合的包裝方式": [
"No matching packing method",
"Tidak ada metode kemas yang cocok"
],
"沒有等著換上的新模型（candidate.pt）": [
"No new model waiting to be switched in (candidate.pt)",
"Tidak ada model baru yang menunggu dipasang (candidate.pt)"
],
"沒有要加入的預框": [
"No pre-boxes to add",
"Tidak ada kotak awal untuk ditambahkan"
],
"沒有變差、而且至少一項依同樣條件變好，算變好。其他算差不多。新物品上次沒有，只顯示這次的成績，不拿來比。": [
"If nothing got worse and at least one item got better by the same rules, it counts as better. Otherwise about the same. New items had no previous result, so only this run's score is shown, not compared.",
"Jika tidak ada yang lebih buruk dan minimal satu barang lebih baik dengan aturan yang sama, dihitung lebih baik. Selain itu dihitung hampir sama. Barang baru belum ada hasil sebelumnya, jadi hanya nilai kali ini yang ditampilkan, tidak dibandingkan."
],
"沒有這個動作": [
"No such action",
"Aksi ini tidak ada"
],
"沒有這個路徑": [
"No such path",
"Path ini tidak ada"
],
"沒比較": [
"Not compared",
"Tidak dibandingkan"
],
"注意": [
"Note",
"Catatan"
],
"注意：來源解析度 {0}x{1} 與專案 resolution ": [
"Note: source resolution {0}x{1} and project resolution ",
"Catatan: resolusi sumber {0}x{1} dan resolution proyek "
],
"混淆矩陣（列=真實, 欄=預測）": [
"Confusion matrix (rows = actual, columns = predicted)",
"Matriks konfusi (baris = aktual, kolom = prediksi)"
],
"清單模式": [
"Checklist mode",
"Mode daftar"
],
"清單裡沒有？用搜尋換 ›": [
"Not in the list? Search to change ›",
"Tidak ada di daftar? Cari untuk ganti ›"
],
"測試 2 秒": [
"Test 2 s",
"Uji 2 dtk"
],
"準備中": [
"Preparing",
"Menyiapkan"
],
"滾輪縮放、Shift＋滾輪左右移；點一下跳到那個時間；拖拉方塊兩邊改頭尾": [
"Scroll to zoom, Shift＋scroll to move left/right; click to jump to that time; drag block edges to change start/end",
"Gulir untuk zoom, Shift＋gulir untuk geser kiri/kanan; klik untuk lompat ke waktu itu; tarik sisi blok untuk ubah awal/akhir"
],
"漏做": [
"Missed",
"Terlewat"
],
"漏做次數": [
"Missed count",
"Jumlah terlewat"
],
"漏做輪": [
"Missed cycles",
"Siklus terlewat"
],
"漏做：": [
"Missed: ",
"Terlewat: "
],
"瀏覽器要先點一下網頁才能出聲。": [
"The browser needs one click on the page before it can make sound.",
"Browser perlu satu klik di halaman sebelum bisa berbunyi."
],
"無": [
"None",
"Tidak ada"
],
"無法建立錄影檔：{0}": [
"Cannot create recording file: {0}",
"Tidak bisa membuat file rekaman: {0}"
],
"無法開啟影片：{0}": [
"Cannot open video: {0}",
"Tidak bisa membuka video: {0}"
],
"無法開啟相機 {0}": [
"Cannot open camera {0}",
"Tidak bisa membuka kamera {0}"
],
"照目前的物品、動作排好步驟，到監控畫面": [
"Arrange steps from current items and actions, go to Monitor screen",
"Susun langkah dari barang dan gerakan sekarang, ke Layar pantau"
],
"照規定：6 碼數字＋空一格＋2 碼數字，例如 310222 01": [
"Required format: 6 digits + one space + 2 digits, e.g. 310222 01",
"Format wajib: 6 angka + 1 spasi + 2 angka, contoh: 310222 01"
],
"片段": [
"Clip",
"Klip"
],
"片段數：{0}": [
"Clips: {0}",
"Jumlah klip: {0}"
],
"物品": [
"Items",
"Barang"
],
"物品 {0} 格會拿去訓練": [
"{0} item frames will be used for training",
"{0} frame barang akan dipakai untuk latih"
],
"物品 {0} 格會拿去訓練；舊版框選 {1} 格不在時間軸上，訓練時一樣會用到": [
"{0} item frames will be used for training; {1} old-style boxed frames are not on the timeline but are also used",
"{0} frame barang dipakai untuk latih; {1} frame kotak versi lama tidak ada di timeline tapi tetap dipakai"
],
"物品、動作都存好再按。沒有動作就直接按；之後改動作不用重訓。": [
"Save items and actions first. If there are no actions, just click; changing actions later needs no retraining.",
"Simpan barang dan gerakan dulu. Kalau tidak ada gerakan, langsung klik; ubah gerakan nanti tidak perlu latih ulang."
],
"物品、動作都存好再按。訓練完自動排好步驟，就可以監控；之後改動作不用重訓。": [
"Save items and actions first. After training, steps are arranged automatically and you can monitor; changing actions later needs no retraining.",
"Simpan barang dan gerakan dulu. Setelah latih, langkah otomatis tersusun dan bisa langsung pantau; ubah gerakan nanti tidak perlu latih ulang."
],
"物品和動作都存好，按「開始訓練」。訓練完自動排好步驟。動作不進模型，之後改動作不用重訓": [
"Save items and actions, then click \"Start training\". Steps are arranged automatically after training. Actions are not in the model, so changing actions later needs no retraining",
"Simpan barang dan gerakan, lalu klik \"Mulai latih\". Setelah latih, langkah otomatis tersusun. Gerakan tidak masuk model, jadi ubah gerakan nanti tidak perlu latih ulang"
],
"物品框選改了，要重新訓練": [
"Item boxes changed, please train again",
"Kotak barang berubah, perlu dilatih ulang"
],
"物品都存好了，下一步標動作（沒有要看手的步驟，下一步直接按開始訓練）": [
"Items are saved. Next, mark actions (if no step needs the hands, just press Start training on the next step)",
"Barang sudah disimpan. Berikutnya tandai gerakan (kalau tidak ada langkah yang perlu tangan, di langkah berikutnya langsung tekan Mulai latih)"
],
"物品：拉時間範圍，再畫一個框": [
"Items: drag a time range, then draw a box",
"Barang: tarik rentang waktu, lalu gambar kotak"
],
"物品：看到「{0}」": [
"Item: sees \"{0}\"",
"Barang: terlihat \"{0}\""
],
"狀態": [
"Status",
"Status"
],
"現場": [
"Live",
"Langsung"
],
"產生 GPU 訓練包": [
"Create GPU training package",
"Buat paket latih GPU"
],
"產生 GPU 訓練包（拿到 GPU 電腦訓練，再匯入）": [
"Create GPU training package (train on a GPU PC, then import)",
"Buat paket latih GPU (latih di PC GPU, lalu impor)"
],
"產生步驟失敗：{0}: {1}": [
"Generating steps failed: {0}: {1}",
"Gagal membuat langkah: {0}: {1}"
],
"產線": [
"Line",
"Lini"
],
"產線名稱 *": [
"Line name *",
"Nama lini *"
],
"產線名稱「{0}」重複": [
"Line name \"{0}\" is duplicated",
"Nama lini \"{0}\" sudah ada"
],
"產線在用": [
"Used by line",
"Dipakai lini"
],
"產線的桌面範圍 {0} 超出這個包裝方式的畫面大小 {1}": [
"Line desk area {0} is outside this packing method's frame size {1}",
"Area meja lini {0} melebihi ukuran layar metode kemas ini {1}"
],
"用 GPU 訓練包訓練出來的 out/best.pt；會用打包時保留的驗證段離線驗證，通過才換上。": [
"out/best.pt trained from the GPU training package; it is verified offline with the segments held out when packaging, and only replaces the model if it passes.",
"out/best.pt hasil latih dari paket latih GPU; diverifikasi offline dengan segmen cadangan saat dikemas, baru dipakai kalau lolos."
],
"用共用硬碟的目前版本換掉本機的": [
"Replace local with the shared drive's current version",
"Ganti versi lokal dengan versi aktif drive bersama"
],
"用新模型重判動作…": [
"Re-checking actions with the new model…",
"Mengecek ulang gerakan dengan model baru…"
],
"用新模型重判動作：{0} 個對不上（共 {1} 個）": [
"Re-check actions with new model: {0} mismatched ({1} total)",
"Cek ulang gerakan dengan model baru: {0} tidak cocok (total {1})"
],
"用新模型重判動作：{0} 個都對得上": [
"Re-check actions with new model: all {0} match",
"Cek ulang gerakan dengan model baru: semua {0} cocok"
],
"用途": [
"Purpose",
"Kegunaan"
],
"畫面上沒有認出要檢查的物品": [
"No items to check recognized on screen",
"Tidak ada barang yang perlu dicek terlihat di layar"
],
"畫面上看到：{0}": [
"Seen on screen: {0}",
"Terlihat di layar: {0}"
],
"的資料。": [
" data.",
" data."
],
"盒內模式不支援自動驗證": [
"In-box mode does not support auto validation",
"Mode dalam kotak tidak mendukung validasi otomatis"
],
"盒內模式不比較": [
"No comparison in in-box mode",
"Mode dalam kotak tidak dibandingkan"
],
"盒內模式不重判": [
"In-box mode is not re-checked",
"Mode dalam kotak tidak dicek ulang"
],
"盒內物品": [
"In-box items",
"Barang dalam kotak"
],
"盒內狀態區": [
"In-box state area",
"Area status dalam kotak"
],
"盒內狀態區（沿用上次位置）": [
"In-box state area (last position kept)",
"Area status dalam kotak (pakai posisi terakhir)"
],
"盒內狀態每次判定寫一列到這個 csv（調範例／規則用）": [
"Write one row per in-box state decision to this csv (for tuning examples/rules)",
"Tulis satu baris per penilaian status dalam kotak ke csv ini (untuk atur contoh/aturan)"
],
"盒內狀態：{0}": [
"In-box state: {0}",
"Status dalam kotak: {0}"
],
"盒子 {0} 秒沒看到（{1} 秒後視為拿走）": [
"Box not seen for {0} s (treated as removed after {1} s)",
"Kotak tidak terlihat {0} detik (dianggap diambil setelah {1} detik)"
],
"盒子暫時沒偵測到": [
"Box temporarily not detected",
"Kotak sementara tidak terdeteksi"
],
"盒子移動中": [
"Box moving",
"Kotak bergerak"
],
"盒子：{0}": [
"Box: {0}",
"Kotak: {0}"
],
"監控": [
"Monitor",
"Pantau"
],
"監控中": [
"Monitoring",
"Sedang dipantau"
],
"監控已在執行中，請先停止": [
"Monitor is already running, please stop it first",
"Pantau sedang berjalan, hentikan dulu"
],
"監控時這一步可能一直判不到：多框幾段這個物品再訓練，或改成框大一點的東西": [
"This step may never be detected during monitoring: box more segments of this item and retrain, or use a larger item to box",
"Langkah ini mungkin tidak pernah terdeteksi saat pantau: gambar kotak di lebih banyak segmen barang ini lalu latih ulang, atau pakai barang yang lebih besar"
],
"監控畫面": [
"Monitor screen",
"Layar pantau"
],
"目前 {0}／{1}": [
"Now {0}/{1}",
"Sekarang {0}/{1}"
],
"目前包裝方式": [
"Current packing method",
"Metode kemas saat ini"
],
"目前在做：<b>{0}</b>": [
"Now doing: <b>{0}</b>",
"Sedang dikerjakan: <b>{0}</b>"
],
"目前時間，可輸入後按 Enter 跳過去": [
"Current time, type and press Enter to jump",
"Waktu sekarang, ketik lalu tekan Enter untuk lompat"
],
"目前模型": [
"Current model",
"Model sekarang"
],
"目前步驟：{0}（{1}/{2}）": [
"Current step: {0} ({1}/{2})",
"Langkah sekarang: {0} ({1}/{2})"
],
"目前版本": [
"Current version",
"Versi aktif"
],
"目前還沒指定包裝方式": [
"No packing method set yet",
"Belum ada metode kemas yang ditentukan"
],
"相機": [
"Camera",
"Kamera"
],
"相機 {0} 開了但讀不到影格": [
"Camera {0} opened but no frames can be read",
"Kamera {0} terbuka tapi frame tidak terbaca"
],
"相機 {0}x{1} @ {2} fps，按「開始錄製」": [
"Camera {0}x{1} @ {2} fps, press \"Start recording\"",
"Kamera {0}x{1} @ {2} fps, tekan \"Mulai rekam\""
],
"相機 {0}：{1}x{2} @ {3} fps": [
"Camera {0}: {1}x{2} @ {3} fps",
"Kamera {0}: {1}x{2} @ {3} fps"
],
"相機來源也用同步偵測（預設相機走背景執行緒、影片檔走同步以便重現）": [
"Camera source also uses sync detection (by default camera runs in a background thread, video files run sync for reproducibility)",
"Sumber kamera juga pakai deteksi sinkron (default kamera jalan di thread latar, file video sinkron agar bisa diulang)"
],
"相機來源（留空＝伺服器記住的那一台）": [
"Camera source (blank = the one the server remembers)",
"Sumber kamera (kosong = yang diingat server)"
],
"相機已在使用中": [
"Camera is already in use",
"Kamera sedang dipakai"
],
"相機斷線": [
"Camera disconnected",
"Kamera terputus"
],
"相機編號（整數）或影片檔路徑": [
"Camera number (integer) or video file path",
"Nomor kamera (angka bulat) atau path file video"
],
"相機還沒開好": [
"Camera not ready yet",
"Kamera belum siap"
],
"相機開不起來：{0}": [
"Camera cannot open: {0}",
"Kamera tidak bisa dibuka: {0}"
],
"相機（編號 0、1… 或 rtsp 網址；密碼只存在這台電腦、畫面上遮成 ***）": [
"Camera (number 0, 1… or rtsp URL; the password stays on this computer and shows as ***)",
"Kamera (nomor 0, 1… atau URL rtsp; sandi hanya disimpan di komputer ini dan tampil sebagai ***)"
],
"看所有版本（載入指定版本、設成目前版本）": [
"View all versions (load a specific version, set current version)",
"Lihat semua versi (muat versi tertentu, atur versi aktif)"
],
"看結果": [
"View result",
"Lihat hasil"
],
"確定要換上比較差的模型？": [
"Really use the worse model?",
"Yakin pakai model yang lebih buruk?"
],
"確認": [
"Confirm",
"Konfirmasi"
],
"確認刪除": [
"Confirm delete",
"Konfirmasi hapus"
],
"確認換線": [
"Confirm line change",
"Konfirmasi ganti lini"
],
"示範影片": [
"Demo video",
"Video contoh"
],
"示範影片播完：完成 {0} 輪、漏做 {1} 輪": [
"Demo video finished: {0} cycles done, {1} cycles missed",
"Video contoh selesai: {0} siklus selesai, {1} siklus terlewat"
],
"示範影片裡手在桌面範圍內的畫面太少，找不到候選步驟": [
"Too few frames with hands on the desk in the demo video to find candidate steps",
"Terlalu sedikit bingkai dengan tangan di area meja pada video contoh untuk mencari kandidat langkah"
],
"秒": [
"s",
"detik"
],
"程式一開、每 10 分鐘、停止監控、換線時上傳；還沒傳成功的日子一起補送。操作 → 今日統計 可以看內容": [
"Uploaded when the program starts, every 10 minutes, on stop monitoring and on line change; days not yet uploaded are sent together. See Actions → Today's stats for details",
"Diupload saat program dibuka, tiap 10 menit, saat berhenti pantau dan saat ganti lini; hari yang belum terkirim dikirim bersama. Lihat isinya di Aksi → Statistik hari ini"
],
"種類只能是 物品 或 動作": [
"Type can only be item or action",
"Jenis hanya boleh barang atau gerakan"
],
"空桌誤報": [
"Empty-desk false alarm",
"Alarm palsu meja kosong"
],
"空桌誤報（上次 → 這次）": [
"Empty-desk false alarm (last → this)",
"Alarm palsu meja kosong (sebelum → sekarang)"
],
"空桌面": [
"Empty desk",
"Meja kosong"
],
"空桌面 {0}": [
"Empty desk {0}",
"Meja kosong {0}"
],
"空桌面不用畫框，按下方「這一格標成空桌面」": [
"No box needed for the empty desk; press \"Mark this frame as empty desk\" below",
"Meja kosong tidak perlu kotak; tekan \"Tandai bingkai ini sebagai meja kosong\" di bawah"
],
"空桌面標好了，下一步框物品": [
"Empty desk marked; next, box the items",
"Meja kosong sudah ditandai; berikutnya beri kotak barang"
],
"空的裁圖": [
"Empty crop",
"Potongan gambar kosong"
],
"立即上傳": [
"Upload now",
"Upload sekarang"
],
"立即上傳（含 {0}）": [
"Upload now (incl. {0})",
"Upload sekarang (termasuk {0})"
],
"站別顯示名稱": [
"Station display name",
"Nama tampilan stasiun"
],
"站別（電腦名稱，自動帶）": [
"Station (computer name, automatic)",
"Stasiun (nama komputer, otomatis)"
],
"第": [
"No. ",
"Ke-"
],
"第 1 段開始": [
"Segment 1 start",
"Mulai segmen 1"
],
"第 2 步：框物品": [
"Step 2: Box items",
"Langkah 2: Beri kotak barang"
],
"第 2 步：標空桌面": [
"Step 2: Mark empty desk",
"Langkah 2: Tandai meja kosong"
],
"第 3 步：框物品": [
"Step 3: Box items",
"Langkah 3: Beri kotak barang"
],
"第 3 步：標動作（沒有就跳過）": [
"Step 3: Mark actions (skip if none)",
"Langkah 3: Tandai gerakan (lewati kalau tidak ada)"
],
"第 4 步：標動作（沒有就跳過）": [
"Step 4: Mark actions (skip if none)",
"Langkah 4: Tandai gerakan (lewati kalau tidak ada)"
],
"第 {0} 格": [
"Frame {0}",
"Frame {0}"
],
"第 {0} 格　{1}": [
"Frame {0}　{1}",
"Frame {0}　{1}"
],
"第 {0} 步沒有名稱": [
"Step {0} has no name",
"Langkah {0} belum ada nama"
],
"第 {0} 步（照已儲存第 1 段的開始時間）": [
"Step {0} (by start time of saved segment 1)",
"Langkah {0} (sesuai waktu mulai segmen 1 yang tersimpan)"
],
"第 {0} 段": [
"Segment {0}",
"Segmen {0}"
],
"第 {0} 段 {1} 到 {2}": [
"Segment {0} {1} to {2}",
"Segmen {0} {1} sampai {2}"
],
"第 {0} 輪　{1}": [
"Cycle {0}　{1}",
"Siklus {0}　{1}"
],
"第 {0} 輪收尾中": [
"Finishing cycle {0}",
"Menyelesaikan siklus {0}"
],
"第 {0} 輪進行中": [
"Cycle {0} in progress",
"Siklus {0} berjalan"
],
"第一次": [
"First time",
"Pertama kali"
],
"第一次訓練，沒有上次可以比，已換上模型。下次訓練會拿這份成績來比。": [
"First training, nothing previous to compare; model is now in use. Next training will compare against this score.",
"Latihan pertama, belum ada hasil sebelumnya; model sudah dipakai. Latihan berikutnya akan dibandingkan dengan nilai ini."
],
"第一次載入約 10～30 秒。": [
"First load takes about 10–30 s.",
"Pertama kali loading sekitar 10–30 detik."
],
"等工作區清空（盒子／鞋子拿走）後開始下一輪": [
"Next cycle starts after the work area is clear (box／shoe removed)",
"Siklus berikutnya mulai setelah area kerja kosong (kotak／sepatu diambil)"
],
"等待開始": [
"Waiting to start",
"Menunggu mulai"
],
"範圍改了，這一段要重新按「儲存這一段」。": [
"Range changed. Click \"Save this segment\" again.",
"Rentang berubah, klik \"Simpan segmen ini\" lagi."
],
"篩選": [
" Filter",
" Filter"
],
"系統會用保留的驗證段離線驗證，通過才換上。\\n\\n": [
"   The system validates offline with the held-out segments and swaps it in only if it passes.\\n\\n",
"   Sistem akan validasi offline dengan segmen validasi yang disimpan, baru diganti kalau lulus.\\n\\n"
],
"組底": [
"Stock fitting",
"Stock fitting"
],
"結尾不能在開頭前面": [
"End cannot be before start",
"Akhir tidak boleh sebelum awal"
],
"結尾拉好了。按「儲存這一段」。": [
"End is set. Click \"Save this segment\".",
"Akhir sudah diatur. Klik \"Simpan segmen ini\"."
],
"結尾拉好了。物品真的離開畫面了嗎？看畫面確認，再按「儲存這一段」。": [
"End is set. Has the item really left the frame? Check the view, then click \"Save this segment\".",
"Akhir sudah diatur. Apakah barang benar-benar sudah keluar layar? Cek layar, lalu klik \"Simpan segmen ini\"."
],
"結束": [
"End",
"Selesai"
],
"結束條件成立 {0}/{1} 秒後結算這一輪": [
"Close this cycle {0}/{1} s after the end condition is met",
"Tutup siklus ini {0}/{1} detik setelah kondisi selesai terpenuhi"
],
"結束條件成立，{0} 秒後結算這一輪": [
"End condition met, closing this cycle in {0} s",
"Kondisi selesai terpenuhi, siklus ini ditutup dalam {0} detik"
],
"編輯": [
"Edit",
"Ubah"
],
"編輯型體地區": [
"Edit Style/Region",
"Ubah Artikel/Wilayah"
],
"縮小時間軸": [
"Zoom out timeline",
"Perkecil timeline"
],
"结束": [
"End",
"Selesai"
],
"考卷：{0} 定的，每個物品取最後一段框，共 {1} 格，加空桌 {2} 格。這些畫面不拿去訓練，新舊模型考同一份。": [
"Test: set {0}, last box segment of each item, {1} frames total, plus {2} empty-desk frames. These frames are not used for training; old and new models take the same test.",
"Tes: dibuat {0}, ambil segmen kotak terakhir tiap barang, total {1} frame, ditambah {2} frame meja kosong. Frame ini tidak dipakai untuk latihan; model lama dan baru ikut tes yang sama."
],
"考完，比上次好，已換上新模型": [
"Test done, better than last time, switched to new model",
"Tes selesai, lebih bagus dari sebelumnya, sudah ganti ke model baru"
],
"考完，跟上次差不多，已換上新模型": [
"Test done, about the same as last time, switched to new model",
"Tes selesai, hampir sama dengan sebelumnya, sudah ganti ke model baru"
],
"考試中：上次的模型…": [
"Testing: previous model…",
"Tes: model sebelumnya…"
],
"考試中：這次的模型…": [
"Testing: this model…",
"Tes: model kali ini…"
],
"考試失敗（{0}: {1}），沒有比較": [
"Test failed ({0}: {1}), no comparison",
"Tes gagal ({0}: {1}), tidak ada perbandingan"
],
"自動": [
"Auto",
"Otomatis"
],
"自動找候選步驟": [
"Find candidate steps automatically",
"Cari kandidat langkah otomatis"
],
"自動找候選步驟失敗：": [
"Finding candidate steps failed: ",
"Gagal mencari kandidat langkah: "
],
"自動找候選步驟：{0}": [
"Finding candidate steps: {0}",
"Mencari kandidat langkah: {0}"
],
"自動標記": [
"Auto label",
"Tandai otomatis"
],
"自動標記要有桌面範圍（固定範圍）：先在「包裝設定（訓練）」存至少一個物品的框，範圍會自動算": [
"Auto label needs a desk area (fixed area): first save at least one item's box in \"Packing setup (training)\"; the area is calculated automatically",
"Tandai otomatis butuh area meja (area tetap): simpan dulu kotak minimal satu barang di \"Pengaturan kemas (latih)\"; area dihitung otomatis"
],
"自動標記要有桌面範圍（固定範圍）：先在「標記物品」存至少一個物品的框，範圍會自動算": [
"Auto label needs a desk area (fixed area): first save at least one item's box in \"Label items\"; the area is calculated automatically",
"Tandai otomatis butuh area meja (area tetap): simpan dulu kotak minimal satu barang di \"Tandai barang\"; area dihitung otomatis"
],
"至少要 {0} 段、{1} 張、{2} 張），先用自己訓練的模型": [
"need at least {0} segments, {1} and {2} images), using your own trained model",
"minimal {0} segmen, {1} dan {2} gambar), pakai model hasil latih sendiri"
],
"蓋上": [
"Close lid",
"Tutup"
],
"蓋著（視同盒子不在）": [
"Covered (treated as no box)",
"Tertutup (dianggap tidak ada kotak)"
],
"藍框＝手框的那一格；其他是自動往前後 2 秒追出來的。框錯的按 ✕ 標成待刪，再按一次（↺）復原；按「套用」才真的刪。": [
"Blue box = the manually boxed frame; others are auto-tracked 2 s before and after. Click ✕ on wrong boxes to mark for deletion, click again (↺) to undo; they are only deleted when you click \"Apply\".",
"Kotak biru = frame yang dikotak manual; lainnya dilacak otomatis 2 detik ke depan dan belakang. Kotak salah klik ✕ untuk tandai hapus, klik lagi (↺) untuk batalkan; baru benar-benar terhapus setelah klik \"Terapkan\"."
],
"處理 {0} fps  t={1}s": [
"Processing {0} fps  t={1}s",
"Memproses {0} fps  t={1}s"
],
"蜂鳴器模式只能是 off／speaker／command": [
"Buzzer mode must be off / speaker / command",
"Mode buzzer hanya boleh off / speaker / command"
],
"蜂鳴器沒有響：{0}": [
"Buzzer did not sound: {0}",
"Buzzer tidak berbunyi: {0}"
],
"蜂鳴器設定": [
"Buzzer settings",
"Pengaturan buzzer"
],
"裁斷": [
"Cutting",
"Cutting"
],
"補傳中 {0}/{1}（{2}）": [
"Resending {0}/{1} ({2})",
"Kirim ulang {0}/{1} ({2})"
],
"補框 第 {0}／{1} 處：第 {2} 輪「{3}」大約在 {4}～{5}。畫面上有的話，在這裡按「從這裡開始」補一段並儲存；真的沒做就跳下一處。": [
"Fill-in box {0}/{1}: Cycle {2} \"{3}\" around {4}～{5}. If it is visible, click \"Start here\" to add a segment and save; if it really was not done, go to the next one.",
"Tambah kotak {0}/{1}: Siklus {2} \"{3}\" sekitar {4}～{5}. Kalau terlihat di layar, klik \"Mulai dari sini\" untuk tambah segmen lalu simpan; kalau memang tidak dikerjakan, lanjut ke berikutnya."
],
"補標記這個配色的畫面後重新訓練": [
"Label more frames for this color and retrain",
"Tandai lagi gambar warna ini lalu latih ulang"
],
"製程類別": [
"Process type",
"Jenis proses"
],
"要刪的框不存在，請重新整理後再試": [
"Box to delete does not exist, please refresh and try again",
"Kotak yang mau dihapus tidak ada, refresh lalu coba lagi"
],
"要刪除這 {0} 個包裝方式嗎": [
"Delete these {0} packing method(s)",
"Hapus {0} metode kemas ini"
],
"要在這一段的範圍裡畫框": [
"Draw the box inside this segment's range",
"Gambar kotak di dalam rentang segmen ini"
],
"視窗數：{0}": [
"Windows: {0}",
"Jumlah jendela: {0}"
],
"解除警告": [
"Clear alarm",
"Matikan alarm"
],
"訂單": [
"Order ",
"Order "
],
"訂單編號放在每一塊的滑鼠提示": [
"Order numbers are in the mouse tooltip of each block",
"Nomor order ada di tooltip mouse tiap blok"
],
"訓練": [
"Train",
"Latih"
],
"訓練 {0}": [
"Train {0}",
"Latih {0}"
],
"訓練中…": [
"Training…",
"Sedang latih…"
],
"訓練中（": [
"Training (",
"Sedang latih ("
],
"訓練圖 {0} 張、驗證圖 {1} 張；保留驗證段 {2} 段（在原電腦驗證）\\n": [
"{0} training images, {1} validation images; {2} held-out validation segments (validated on the original computer)\\n",
"{0} gambar latih, {1} gambar validasi; {2} segmen validasi disimpan (divalidasi di komputer asal)\\n"
],
"訓練失敗（結束碼 {0}）：": [
"Training failed (exit code {0}): ",
"Latih gagal (kode keluar {0}): "
],
"訓練完成": [
"Training done",
"Latih selesai"
],
"訓練完成，已換上新模型": [
"Training done, switched to new model",
"Latih selesai, sudah ganti ke model baru"
],
"訓練完成，已換上模型（第一次，沒有上次可比）": [
"Training done, model installed (first time, nothing to compare)",
"Latih selesai, model sudah dipasang (pertama kali, tidak ada pembanding)"
],
"訓練時間": [
"Training time",
"Waktu latih"
],
"訓練模型中（約 20～60 分鐘）…": [
"Training model (about 20–60 minutes)…",
"Melatih model (sekitar 20–60 menit)…"
],
"訓練素材已選 {0} / {1} 段": [
"Training material: {0} / {1} segments selected",
"Materi latih: {0} / {1} segmen dipilih"
],
"訓練素材範圍": [
"Training material scope",
"Cakupan materi latih"
],
"訓練素材預覽": [
"Training material preview",
"Pratinjau materi latih"
],
"訓練素材預覽　{0}／{1}　配色 {2}": [
"Training material preview　{0}／{1}　color {2}",
"Pratinjau materi latih　{0}／{1}　warna {2}"
],
"訓練結果": [
"Training result　",
"Hasil latih　"
],
"訓練辨識模型": [
"Train recognition model",
"Latih model pengenal"
],
"設定": [
"Settings",
"Pengaturan"
],
"設定型體地區": [
"Set Style/Region",
"Atur Artikel/Wilayah"
],
"設定檔有問題": [
"Settings file has a problem",
"File pengaturan bermasalah"
],
"設成目前版本": [
"Make current version",
"Jadikan versi saat ini"
],
"設為盒子的樣子（看到它就算盒子還在桌上，推走才算一輪結束）": [
"Set as the box look (while seen, the box is still on the desk; a cycle ends only when it is pushed away)",
"Jadikan bentuk kotak (selama terlihat, kotak dianggap masih di meja; satu siklus selesai setelah didorong pergi)"
],
"試跑": [
"Test run",
"Uji coba"
],
"試跑中：配色「{0}」模型還沒驗證過。照樣判斷與顯示漏做，但不計入錯誤率、不響警報。請錄 2～3 輪後到「包裝方式設定 → 辨識模型」驗證。": [
"Trial run: model for color \"{0}\" is not verified yet. Missed steps are still checked and shown, but not counted in the error rate and no alarm. Record 2–3 cycles, then verify in \"Packing method settings → Recognition model\".",
"Uji coba: model untuk warna \"{0}\" belum diverifikasi. Langkah terlewat tetap dicek dan ditampilkan, tapi tidak dihitung ke tingkat kesalahan dan alarm tidak bunyi. Rekam 2–3 siklus, lalu verifikasi di \"Pengaturan metode kemas → Model pengenalan\"."
],
"試跑中：配色「{0}」模型還沒驗證過。照樣判斷與顯示漏做，但不計入錯誤率、不響警報。請錄 2～3 輪後到「包裝明細 → 辨識模型」驗證。": [
"Trial run: model for color \"{0}\" is not verified yet. Missed steps are still checked and shown, but not counted in the error rate and no alarm. Record 2–3 cycles, then verify in \"Packing details → Recognition model\".",
"Uji coba: model untuk warna \"{0}\" belum diverifikasi. Langkah terlewat tetap dicek dan ditampilkan, tapi tidak dihitung ke tingkat kesalahan dan alarm tidak bunyi. Rekam 2–3 siklus, lalu verifikasi di \"Rincian kemas → Model pengenalan\"."
],
"試跑，不計入錯誤率": [
"Trial run, not counted in error rate",
"Uji coba, tidak dihitung ke tingkat kesalahan"
],
"語言只能選": [
"Language must be one of",
"Bahasa hanya bisa"
],
"說明": [
"Help",
"Keterangan"
],
"請先勾選要留下的候選步驟": [
"Tick the candidate steps to keep first",
"Centang dulu kandidat langkah yang ingin disimpan"
],
"請先在左邊選一個包裝方式": [
"Please select a packing method on the left first",
"Pilih dulu metode kemas di kiri"
],
"請先在畫面上拖拉框住物品": [
"Drag on the screen to box the item first",
"Seret di layar untuk mengotak barang dulu"
],
"請先輸入名稱": [
"Please enter a name first",
"Masukkan nama dulu"
],
"請先選 GPU 訓練出來的 best.pt": [
"Please select the GPU-trained best.pt first",
"Pilih dulu best.pt hasil latih GPU"
],
"請先選一個有示範影片的專案": [
"Pick a project that has a demo video first",
"Pilih dulu proyek yang punya video contoh"
],
"請先選影片檔": [
"Please select a video file first",
"Pilih file video dulu"
],
"請勾選要刪除的包裝方式": [
"Select the packing methods to delete",
"Pilih metode kemas yang akan dihapus"
],
"請回時間軸多標幾段（影片太短就重錄一段 60 秒左右、每個動作做 3 次以上）。": [
"Go back to the timeline and label more segments (if the video is too short, record about 60 s again and do each action 3+ times).",
"Kembali ke timeline dan tandai lebih banyak segmen (kalau video terlalu pendek, rekam ulang sekitar 60 detik dan lakukan tiap gerakan 3 kali atau lebih)."
],
"請在左邊選一個包裝方式": [
"Please select a packing method on the left",
"Pilih metode kemas di kiri"
],
"請在畫面上拖拉框住物品（框太小）": [
"Drag on the screen to box the item (box too small)",
"Seret di layar untuk mengotak barang (kotak terlalu kecil)"
],
"請填共用硬碟資料夾": [
"Enter the shared drive folder",
"Isi folder drive bersama"
],
"請填產線名稱": [
"Please enter the line name",
"Isi nama lini"
],
"請確認監控程式還開著": [
"Please check that the monitoring program is still open",
"Pastikan program pantau masih terbuka"
],
"請至少勾一段訓練素材": [
"Select at least one training segment",
"Pilih minimal satu segmen bahan latih"
],
"請至少勾選一個候選步驟並取名": [
"Tick at least one candidate step and name it",
"Centang minimal satu kandidat langkah dan beri nama"
],
"請輸入密碼": [
"Enter the password",
"Masukkan password"
],
"請輸入步驟名稱和物件的英文提示（例如 shoe）": [
"Enter the step name and an English prompt for the object (e.g. shoe)",
"Masukkan nama langkah dan prompt bahasa Inggris untuk objek (misalnya shoe)"
],
"請輸入物品名稱": [
"Please enter an item name",
"Masukkan nama barang"
],
"請輸入產線名稱": [
"Please enter a line name",
"Masukkan nama lini"
],
"請輸入配色名稱": [
"Enter a colorway name",
"Isi nama warna"
],
"請選 best.pt": [
"Choose best.pt",
"Pilih best.pt"
],
"警告": [
"Warning",
"Peringatan"
],
"警告後幾秒自動 reset（開發用）": [
"Auto reset N seconds after warning (dev only)",
"Reset otomatis N detik setelah peringatan (untuk dev)"
],
"讀不到 EIP 產線：": [
"Cannot read EIP lines: ",
"Tidak bisa baca lini EIP: "
],
"讀不到第 {0} 格：{1}": [
"Cannot read frame {0}: {1}",
"Tidak bisa baca frame {0}: {1}"
],
"讀取 EIP 產線清單中…": [
"Loading EIP line list…",
"Memuat daftar lini EIP…"
],
"變好": [
"Better",
"Lebih baik"
],
"變差": [
"Worse",
"Lebih buruk"
],
"貼好的貼紙連盒邊一起框、放好的鞋子連盒蓋一起框。只框東西本身，它還在旁邊沒做完時也會被算成做完。": [
"Box an applied sticker together with the box edge, and a placed shoe together with the box lid. If you box only the thing itself, it will count as done even while it is still lying beside the box unfinished.",
"Beri kotak stiker yang sudah ditempel bersama sisi kotak, dan sepatu yang sudah ditaruh bersama tutup kotak. Kalau hanya barangnya saja yang diberi kotak, saat masih di samping dan belum selesai pun akan dihitung selesai."
],
"資料不夠（{0} 段、驗收正例 {1} 張、反例 {2} 張；": [
"Not enough data ({0} segments, {1} positive and {2} negative test images; ",
"Data kurang ({0} segmen, {1} gambar positif dan {2} gambar negatif untuk tes; "
],
"超時": [
"Overtime",
"Lewat waktu"
],
"超時 {0} 輪": [
"Overtime {0} cycles",
"Lewat waktu {0} siklus"
],
"跑這麼多秒就停，0 = 不限": [
"Stop after this many seconds, 0 = no limit",
"Berhenti setelah sekian detik, 0 = tanpa batas"
],
"跟「{0}」第 {1} 段重疊了（同一個名稱同一時間只能有一段）": [
"Overlaps \"{0}\" segment {1} (one name can only have one segment at a time)",
"Tumpang tindih dengan \"{0}\" segmen {1} (satu nama hanya boleh satu segmen di waktu yang sama)"
],
"跟上次差不多，已換上新模型。上次的模型存成 best_prev_<時間>.pt。": [
"About the same as last time; new model is now in use. Previous model saved as best_prev_<time>.pt.",
"Hampir sama dengan sebelumnya; model baru sudah dipakai. Model sebelumnya disimpan sebagai best_prev_<waktu>.pt."
],
"跳步": [
"Skipped step",
"Lompat langkah"
],
"跳步 {0} 輪": [
"Skipped steps {0} cycles",
"Lompat langkah {0} siklus"
],
"載入中": [
"Loading",
"Memuat"
],
"載入中 1/4：手部模型…": [
"Loading 1/4: hand model…",
"Memuat 1/4: model tangan…"
],
"載入中 2/4：物件偵測模型（YOLO）…": [
"Loading 2/4: object detection model (YOLO)…",
"Memuat 2/4: model deteksi objek (YOLO)…"
],
"載入中 3/4：物品／狀態辨識模型…": [
"Loading 3/4: item／state recognition model…",
"Memuat 3/4: model pengenalan barang／kondisi…"
],
"載入中 4/4：開啟": [
"Loading 4/4: opening",
"Memuat 4/4: membuka"
],
"載入中…": [
"Loading…",
"Memuat…"
],
"載入中（第一次約 10～30 秒，請等畫面出現）…": [
"Loading (first time about 10–30 s, please wait for the screen)…",
"Memuat (pertama kali sekitar 10–30 detik, tunggu layar muncul)…"
],
"載入到這台電腦": [
"Load to this computer",
"Muat ke komputer ini"
],
"載入專案失敗：{0}": [
"Failed to load project: {0}",
"Gagal memuat proyek: {0}"
],
"載入目前版本到這台電腦": [
"Load current version to this computer",
"Muat versi aktif ke komputer ini"
],
"載入＝把共用硬碟上那一版的設定、步驟、框、辨識模型複製到這台電腦，不用重訓。載入後到監控畫面「操作 → 換包裝方式」就能選。共用硬碟的檔案不會被改。": [
"Load = copy that version's settings, steps, boxes and recognition model from the shared drive to this computer; no retraining needed. After loading, choose it in the Monitor screen under \"Actions → Change packing method\". Files on the shared drive are not changed.",
"Muat = salin pengaturan, langkah, kotak, dan model pengenalan versi itu dari drive bersama ke komputer ini, tanpa latih ulang. Setelah dimuat, pilih di Layar pantau lewat \"Aksi → Ganti metode kemas\". File di drive bersama tidak diubah."
],
"輪": [
" cycles",
" siklus"
],
"辨識模型": [
"Recognition model",
"Model pengenalan"
],
"辨識模型還沒訓練，或還沒設定型體地區": [
"Recognition model not trained yet, or Style/Region not set",
"Model pengenal belum dilatih, atau Artikel/Wilayah belum diatur"
],
"辨識速度只有 {0} fps，判斷可能會延遲": [
"Recognition speed is only {0} fps, results may be delayed",
"Kecepatan pengenalan hanya {0} fps, hasil bisa terlambat"
],
"追蹤整段中…（幾秒到幾十秒，看段落長度）": [
"Tracking the whole segment… (seconds to tens of seconds, depending on length)",
"Melacak seluruh segmen… (beberapa detik sampai puluhan detik, tergantung panjang segmen)"
],
"逐格畫面": [
"Frame by frame",
"Per frame"
],
"這一格在「{0}」的段落裡，桌上有東西；換一格什麼都沒有的": [
"This frame is inside a \"{0}\" segment, so something is on the desk; pick a frame with nothing on it",
"Bingkai ini ada di segmen \"{0}\", jadi ada barang di meja; pilih bingkai yang kosong"
],
"這一格已標成空桌面": [
"This frame is marked as empty desk",
"Bingkai ini sudah ditandai meja kosong"
],
"這一格桌上什麼都沒有（盒子、鞋子都還沒放上來）": [
"Nothing is on the desk in this frame (no box or shoes yet)",
"Tidak ada apa pun di meja pada bingkai ini (belum ada kotak atau sepatu)"
],
"這一格標成空桌面": [
"Mark this frame as empty desk",
"Tandai bingkai ini sebagai meja kosong"
],
"這一格沒追到，可再框一次": [
"This frame was not tracked, you can box it again",
"Frame ini tidak terlacak, bisa beri kotak lagi"
],
"這一步看手停在物件上，不用框；常沒看到的話調整停留秒數": [
"This step checks the hand resting on the item, no box needed; if often not seen, adjust hold time",
"Langkah ini melihat tangan diam di barang, tidak perlu kotak; kalau sering tidak terlihat, ubah lama diam"
],
"這一段已經不存在了，請重新整理": [
"This segment no longer exists, please refresh",
"Segmen ini sudah tidak ada, silakan refresh"
],
"這一段還沒畫框。把時間移到這一段裡面，在畫面上拖拉框住「{0}」": [
"This segment has no box yet. Move the time inside this segment and drag on the screen to box \"{0}\"",
"Segmen ini belum ada kotak. Geser waktu ke dalam segmen ini, lalu seret di layar untuk mengotak \"{0}\""
],
"這一段還沒畫框。把時間移到這一段裡面，在畫面上拖拉框住「{0}」。": [
"This segment has no box yet. Move the time into this segment and drag a box around \"{0}\" on the view.",
"Segmen ini belum ada kotak. Pindahkan waktu ke dalam segmen ini, lalu tarik kotak di sekitar \"{0}\" di layar."
],
"這一輪已經 {0} 秒，超過 {1} 秒會報超時": [
"This cycle has run {0} s, over {1} s will be reported as Overtime",
"Siklus ini sudah {0} detik, lebih dari {1} detik akan dilaporkan Lewat waktu"
],
"這一輪待刪 {0} 格": [
"{0} frames pending delete in this cycle",
"{0} frame akan dihapus di siklus ini"
],
"這一輪還沒有框選。點左邊紅色的步驟，或上方「到標記頁補框」。": [
"This cycle has no boxes yet. Click a red step on the left, or \"Add boxes on the label page\" above.",
"Siklus ini belum ada kotak. Klik langkah merah di kiri, atau \"Tambah kotak di halaman tandai\" di atas."
],
"這一輪還沒框選，不能拿來訓練": [
"This cycle has no boxes yet, cannot be used for training",
"Siklus ini belum ada kotak, tidak bisa dipakai latih"
],
"這不像 YOLO 的 best.pt（檔案太小或格式不對）": [
"This does not look like a YOLO best.pt (file too small or wrong format)",
"Ini tidak seperti best.pt YOLO (file terlalu kecil atau format salah)"
],
"這些門檻是先訂的數字，還沒用現場資料調過；考題 20 格時，差 1 格就差 5 點，所以另外要求至少差幾格。": [
"These thresholds are preset numbers, not yet tuned with real line data. With a 20-frame test, 1 frame = 5 pts, so a minimum frame difference is also required.",
"Ambang ini angka awal, belum disesuaikan dengan data lapangan. Dengan tes 20 frame, beda 1 frame = 5 poin, jadi juga diminta beda frame minimal."
],
"這個包裝方式已停用": [
"This packing method is disabled",
"Metode kemas ini dinonaktifkan"
],
"這個包裝方式的辨識模型還沒訓練，不能用來監控": [
"This packing method's recognition model is not trained yet, cannot be used to monitor",
"Model pengenalan metode kemas ini belum dilatih, tidak bisa dipakai untuk pantau"
],
"這個包裝方式還沒有步驟": [
"This packing method has no steps yet",
"Metode kemas ini belum punya langkah"
],
"這個專案沒有示範影片": [
"This project has no demo video",
"Proyek ini tidak punya video contoh"
],
"這個專案還沒有可用的辨識模型": [
"This project has no usable detection model yet",
"Proyek ini belum punya model deteksi yang bisa dipakai"
],
"這個專案還沒有步驟": [
"This project has no steps yet",
"Proyek ini belum punya langkah"
],
"這個專案還沒有步驟。到「包裝設定（訓練）」訓練，訓練完會自動排好。": [
"This project has no steps yet. Train in \"Packing setup (training)\"; steps are arranged automatically after training.",
"Proyek ini belum ada langkah. Latih di \"Pengaturan kemas (latih)\", setelah latih langkah otomatis disusun."
],
"這個專案還沒有步驟。到「標記物品」訓練，訓練完會自動排好。": [
"This project has no steps yet. Train in \"Label items\"; steps are arranged automatically after training.",
"Proyek ini belum ada langkah. Latih di \"Tandai barang\", setelah latih langkah otomatis disusun."
],
"這個專案還沒有步驟，請先在桌面程式的「② 標記物品」產生步驟": [
"This project has no steps yet. Generate steps in the desktop app under \"② Label items\" first",
"Proyek ini belum punya langkah. Buat langkah dulu di aplikasi desktop pada \"② Tandai barang\""
],
"這個專案還沒有示範影片": [
"This project has no demo video yet",
"Proyek ini belum punya video contoh"
],
"這個專案還沒有示範影片，先用下面任一種方式準備": [
"This project has no demo video yet. Prepare one using either method below",
"Proyek ini belum punya video contoh. Siapkan dengan salah satu cara di bawah"
],
"這個專案還沒有訓練好的模型，請先手動框幾個樣本並訓練一次": [
"This project has no trained model yet. Box a few samples by hand and train once first",
"Proyek ini belum punya model terlatih. Kotak beberapa contoh manual dan latih sekali dulu"
],
"這個專案還沒有辨識模型。到「包裝設定（訓練）」框選物品後按「開始訓練」。": [
"This project has no recognition model yet. Go to \"Packing setup (training)\", draw boxes on items and click \"Start training\".",
"Proyek ini belum punya model pengenal. Ke \"Pengaturan kemas (latih)\", gambar kotak pada barang lalu klik \"Mulai latih\"."
],
"這個專案還沒有辨識模型。到「標記物品」框選物品後按「開始訓練」。": [
"This project has no recognition model yet. Go to \"Label items\", draw boxes on items and click \"Start training\".",
"Proyek ini belum punya model pengenal. Ke \"Tandai barang\", gambar kotak pada barang lalu klik \"Mulai latih\"."
],
"這個專案還沒設定型體地區": [
"This project has no style/region set yet",
"Proyek ini belum diatur artikel/wilayahnya"
],
"這個專案還沒設定型體地區。按左邊鉛筆圖示設定。": [
"This project has no Style/Region yet. Click the pencil icon on the left to set it.",
"Proyek ini belum diatur Artikel/Wilayah. Klik ikon pensil di kiri untuk mengatur."
],
"這個時間點不在任何一段裡。先按「從這裡開始」新增一段，再畫框。": [
"This time is not in any segment. Click \"Start here\" to add a segment first, then draw a box.",
"Waktu ini tidak ada di segmen mana pun. Klik \"Mulai dari sini\" untuk tambah segmen dulu, lalu gambar kotak."
],
"這個網頁不會出聲。": [
"This page will not make sound.",
"Halaman ini tidak akan berbunyi."
],
"這個網頁：警告時一直嗶嗶叫": [
"This page: keep beeping during alerts",
"Halaman ini: terus berbunyi saat peringatan"
],
"這台電腦的產線": [
"This computer's line",
"Lini komputer ini"
],
"這台電腦的產線設定": [
"Line settings for this PC",
"Pengaturan lini PC ini"
],
"這台電腦的產線設定（相機、EIP）": [
"Line settings for this computer (camera, EIP)",
"Pengaturan lini komputer ini (kamera, EIP)"
],
"這台電腦還沒有專案": [
"No projects on this computer yet",
"Belum ada proyek di komputer ini"
],
"這台電腦還沒設好產線或相機，按這裡設定": [
"This computer has no line or camera set yet. Click here to set up",
"Komputer ini belum diatur lini atau kameranya. Klik di sini untuk atur"
],
"這幾秒沒偵測到手。確認範圍有拉到手在做動作的時候、手沒有被遮住。": [
"No hand detected in these seconds. Make sure the range covers when the hand is working and the hand is not hidden.",
"Tidak ada tangan terdeteksi di detik ini. Pastikan rentang mencakup saat tangan bekerja dan tangan tidak tertutup."
],
"這幾秒畫面上沒有任何已框的物品。先框一個被手碰到的東西（例如 鞋子）並儲存，再存這個動作。": [
"No boxed items on screen in these seconds. First box something the hand touches (e.g. shoe) and save, then save this action.",
"Tidak ada barang yang dikotak di layar pada detik ini. Kotak dulu barang yang disentuh tangan (misalnya sepatu) dan simpan, lalu simpan gerakan ini."
],
"這支影片還沒有框選，也還沒分析步驟。按上方「分析步驟」，系統會自動切出每一輪。": [
"This video has no boxes and no step analysis yet. Click \"Analyze steps\" above and the system will auto-split each cycle.",
"Video ini belum ada kotak dan belum dianalisis langkahnya. Klik \"Analisis langkah\" di atas, sistem akan otomatis potong tiap siklus."
],
"這是盒子的樣子：看到它就算盒子還在桌上，推走才算一輪結束（再按一次取消）": [
"This is the box look: while seen, the box is still on the desk; a cycle ends only when it is pushed away (click again to cancel)",
"Ini bentuk kotak: selama terlihat, kotak dianggap masih di meja; satu siklus selesai setelah didorong pergi (klik lagi untuk batal)"
],
"這條產線已停用": [
"This line is disabled",
"Lini ini dinonaktifkan"
],
"這條產線正在監控中，請先停止": [
"This line is being monitored, stop it first",
"Lini ini sedang dipantau, hentikan dulu"
],
"這條線正在監控中。換線會重新載入模型（約 10～30 秒），目前這一輪作廢，不結算也不報警。": [
"This line is being monitored. Changing line reloads the model (about 10–30 s); the current cycle is discarded, not counted and no alarm.",
"Lini ini sedang dipantau. Ganti lini akan memuat ulang model (sekitar 10–30 detik); siklus sekarang dibatalkan, tidak dihitung dan tidak ada alarm."
],
"這次比上次": [
"This time vs. last",
"Kali ini dibanding sebelumnya"
],
"這次警告不再叫（只關這個網頁的聲音）": [
"Stop beeping for this alert (this page only)",
"Hentikan bunyi untuk peringatan ini (hanya halaman ini)"
],
"這版改了什麼（選填，寫進版本紀錄）": [
"What changed in this version (optional, saved in the version log)",
"Apa yang berubah di versi ini (opsional, dicatat di riwayat versi)"
],
"這裡已經有一段了，已經幫你選取它。": [
"There is already a segment here; it has been selected for you.",
"Di sini sudah ada segmen, sudah dipilihkan untukmu."
],
"通用辨識可以用：{0}；驗收段找到 {1}、誤報 {2}": [
"General recognition can be used: {0}; test segments found {1}, false alarms {2}",
"Pengenalan umum bisa dipakai: {0}; segmen tes ditemukan {1}, alarm palsu {2}"
],
"通用辨識考不過（最好的是 {0}：驗收段找到 {1}、誤報 {2}；": [
"General recognition failed the test (best was {0}: test segments found {1}, false alarms {2}; ",
"Pengenalan umum gagal tes (terbaik {0}: segmen tes ditemukan {1}, alarm palsu {2}; "
],
"連不上 EIP": [
"Cannot connect to EIP",
"Tidak bisa terhubung ke EIP"
],
"連不上 EIP，也還沒有拿到過今天的資料": [
"Cannot connect to EIP and no data for today received yet",
"Tidak terhubung ke EIP dan belum pernah dapat data hari ini"
],
"連不上伺服器": [
"Cannot connect to server",
"Tidak terhubung ke server"
],
"連不到 {0}，檢查網路或路徑": [
"Cannot connect to {0}, check the network or path",
"Tidak bisa terhubung ke {0}, cek jaringan atau path"
],
"連示範影片一起（要在別台補框或訓練才需要）": [
"Include the demo video (only needed to add boxes or train on another computer)",
"Sertakan video contoh (hanya perlu untuk tambah kotak atau latih di komputer lain)"
],
"進度": [
"Progress",
"Progres"
],
"進階訓練（GPU 等）": [
"Advanced training (GPU, etc.)",
"Latih lanjutan (GPU, dll.)"
],
"選了廠別才讀得到 EIP 產線": [
"Select a factory first to load EIP lines",
"Pilih pabrik dulu untuk memuat lini EIP"
],
"選到的包裝方式": [
"Selected packing method",
"Metode kemas terpilih"
],
"選取片段": [
"Select clip",
"Pilih klip"
],
"選取這一段做訓練素材": [
"Use this segment as training material",
"Pakai segmen ini sebagai materi latih"
],
"選好產線與來源，按「操作 ▾ → 啟動監控」": [
"Choose the line and source, then press \"Actions ▾ → Start monitoring\"",
"Pilih lini dan sumber, lalu tekan \"Aksi ▾ → Mulai pantau\""
],
"選好產線與來源，按「操作 ▾ → 啟動監控」。": [
"Choose the line and source, then press \"Actions ▾ → Start monitoring\".",
"Pilih lini dan sumber, lalu tekan \"Aksi ▾ → Mulai pantau\"."
],
"選配": [
"Optional",
"Opsional"
],
"遺漏步驟：{0}": [
"Missed steps: {0}",
"Langkah terlewat: {0}"
],
"還原": [
"Reset",
"Reset"
],
"還原整個畫面（快速鍵 0）": [
"Reset the whole view (shortcut 0)",
"Reset seluruh tampilan (tombol 0)"
],
"還有 {0} 段沒儲存，沒儲存的不會拿去訓練。要直接開始訓練嗎？": [
"{0} segments are not saved; unsaved ones will not be used for training. Start training anyway?",
"Ada {0} segmen belum disimpan, yang belum disimpan tidak dipakai untuk latih. Tetap mulai latih?"
],
"還沒上傳": [
"Not uploaded yet",
"Belum diunggah"
],
"還沒上傳成功：{0}": [
"Not uploaded yet: {0}",
"Belum terupload: {0}"
],
"還沒分析步驟。按「分析步驟」會用目前的模型把整支影片跑一遍（這台約 {0} 分鐘），之後時間軸會標出每一步的時間、沒看到的步驟會標紅。": [
"Steps not analyzed yet. \"Analyze steps\" runs the current model over the whole video (about {0} min on this PC); then the timeline marks each step's time and unseen steps in red.",
"Langkah belum dianalisis. \"Analisis langkah\" menjalankan model sekarang di seluruh video (sekitar {0} menit di PC ini); lalu timeline menandai waktu tiap langkah, langkah yang tidak terlihat ditandai merah."
],
"還沒拿到資料": [
"No data yet",
"Belum ada data"
],
"還沒指定包裝方式": [
"No packing method set",
"Metode kemas belum ditentukan"
],
"還沒有任何分段標記": [
"No segments labeled yet",
"Belum ada segmen yang ditandai"
],
"還沒有任何專案：到「新增包裝方式」，或「操作 → 共用硬碟」載入": [
"No projects yet: go to \"Add packing method\", or load from \"Actions → Shared drive\"",
"Belum ada proyek: ke \"Tambah metode kemas\", atau muat dari \"Aksi → Drive bersama\""
],
"還沒有儲存的段落，還沒有順序": [
"No saved segments yet, so no order yet",
"Belum ada segmen tersimpan, jadi belum ada urutan"
],
"還沒有動作": [
"No actions yet",
"Belum ada gerakan"
],
"還沒有包裝方式，要先標記、訓練": [
"No packing method yet, label items and train first",
"Belum ada metode kemas, tandai barang dan latih dulu"
],
"還沒有可以監控的包裝方式：要有步驟、而且模型訓練好": [
"No packing method ready to monitor: it needs steps and a trained model",
"Belum ada metode kemas yang bisa dipantau: harus punya langkah dan model yang sudah dilatih"
],
"還沒有可以看的段": [
"No segments to view yet",
"Belum ada segmen untuk dilihat"
],
"還沒有完成任何一輪": [
"No cycle completed yet",
"Belum ada siklus yang selesai"
],
"還沒有框選任何物品": [
"No items boxed yet",
"Belum ada barang yang dikotak"
],
"還沒有步驟。到「包裝設定（訓練）」訓練，訓練完會自動排好。": [
"No steps yet. Train in \"Packing setup (training)\"; steps are arranged automatically after training.",
"Belum ada langkah. Latih di \"Pengaturan kemas (latih)\", setelah latih langkah otomatis disusun."
],
"還沒有步驟。到「標記物品」訓練，訓練完會自動排好。": [
"No steps yet. Train in \"Label items\"; steps are arranged automatically after training.",
"Belum ada langkah. Latih di \"Tandai barang\", setelah latih langkah otomatis disusun."
],
"還沒有段落。移到它出現的地方，按時間軸的「從這裡開始」": [
"No segments yet. Move to where it appears and click \"Start here\" on the timeline",
"Belum ada segmen. Pindah ke tempat ia muncul, klik \"Mulai dari sini\" di timeline"
],
"還沒有物品": [
"No items yet",
"Belum ada barang"
],
"還沒有監控畫面": [
"No monitor screen yet",
"Belum ada layar pantau"
],
"還沒有空桌面": [
"No empty-desk frames yet",
"Belum ada bingkai meja kosong"
],
"還沒有自動找步驟的結果": [
"No automatic step-finding result yet",
"Belum ada hasil pencarian langkah otomatis"
],
"還沒有要上傳的": [
"Nothing to upload",
"Tidak ada yang perlu diupload"
],
"還沒有訓練好的物品模型，請先回第 2 步訓練": [
"No trained item model yet, go back to step 2 and train first",
"Belum ada model barang terlatih, kembali ke langkah 2 dan latih dulu"
],
"還沒有配色紀錄。換線時選的配色會自動記進來（未驗證）。": [
"No color records yet. Colors chosen when changing lines are recorded automatically (not verified).",
"Belum ada catatan warna. Warna yang dipilih saat ganti lini otomatis tercatat (belum diverifikasi)."
],
"還沒框選": [
"No boxes yet",
"Belum ada kotak"
],
"還沒框選，不能拿來訓練；步驟分析切出 {0} 輪，按預覽看每輪缺哪些步驟、再補框": [
"No boxes yet, cannot be used for training; step analysis split {0} cycles, click Preview to see which steps each cycle is missing, then add boxes",
"Belum ada kotak, tidak bisa dipakai latih; analisis langkah memotong {0} siklus, klik Pratinjau untuk lihat langkah yang kurang tiap siklus, lalu tambah kotak"
],
"還沒訓練": [
"Not trained",
"Belum dilatih"
],
"還沒訓練（到「包裝設定（訓練）」按「開始訓練」）": [
"Not trained yet (go to \"Packing setup (training)\" and click \"Start training\")",
"Belum dilatih (ke \"Pengaturan kemas (latih)\" lalu klik \"Mulai latih\")"
],
"還沒訓練（到「標記物品」按「開始訓練」）": [
"Not trained yet (go to \"Label items\" and click \"Start training\")",
"Belum dilatih (ke \"Tandai barang\" lalu klik \"Mulai latih\")"
],
"還沒設定": [
"Not set",
"Belum diatur"
],
"還沒設定 EIP 網址（eip_api.txt）": [
"EIP URL not set yet (eip_api.txt)",
"URL EIP belum diatur (eip_api.txt)"
],
"還沒設定共用硬碟資料夾": [
"Shared drive folder not set yet",
"Folder drive bersama belum diatur"
],
"還沒設定型體地區": [
"Style regions not set",
"Wilayah artikel belum diatur"
],
"還沒設定相機": [
"Camera not set",
"Kamera belum diatur"
],
"還沒選": [
"Not selected",
"Belum dipilih"
],
"配色": [
"Color",
"Warna"
],
"配色「{0}」重複": [
"Colorway \"{0}\" is duplicated",
"Warna \"{0}\" duplikat"
],
"配色驗證": [
"Color check",
"Cek warna"
],
"重判失敗（{0}: {1}）": [
"Re-check failed ({0}: {1})",
"Cek ulang gagal ({0}: {1})"
],
"重新分析": [
"Re-analyze",
"Analisis ulang"
],
"重新分析會覆蓋目前的候選清單（已套用的段落不受影響），確定嗎？": [
"Re-analysing replaces the current candidate list (segments already applied are kept). Continue?",
"Analisis ulang akan mengganti daftar kandidat saat ini (segmen yang sudah diterapkan tetap ada). Lanjutkan?"
],
"重新找候選步驟": [
"Find candidate steps again",
"Cari ulang kandidat langkah"
],
"重新訓練": [
"Retrain",
"Latih ulang"
],
"重新訓練（{0}）": [
"Retrain ({0})",
"Latih ulang ({0})"
],
"重置區": [
"Reset zone",
"Area reset"
],
"針車": [
"Sewing",
"Jahit"
],
"錄好了：{0} 格。": [
"Recorded: {0} frames.",
"Selesai rekam: {0} frame."
],
"錯誤": [
"Error",
"Salah"
],
"錯誤率 {0}%": [
"Error rate {0}%",
"Tingkat kesalahan {0}%"
],
"錯誤：": [
"Error: ",
"Error: "
],
"門檻是找到 ≥ {0}、誤報 ≤ {1}），用自己訓練的模型": [
"pass mark is found ≥ {0}, false alarms ≤ {1}), using your own trained model",
"syarat lulus ditemukan ≥ {0}, alarm palsu ≤ {1}), pakai model hasil latih sendiri"
],
"開 OpenCV 視窗顯示（只畫 ASCII）": [
"Show OpenCV window (ASCII only)",
"Tampilkan jendela OpenCV (hanya ASCII)"
],
"開啟相機中…": [
"Opening camera…",
"Membuka kamera…"
],
"開啟相機預覽": [
"Open camera preview",
"Buka pratinjau kamera"
],
"開始分析步驟": [
"Start analyzing steps",
"Mulai analisis langkah"
],
"開始分析示範影片，約 2～4 分鐘，好了會自動跳出候選清單": [
"Analysing the demo video, about 2–4 minutes; the candidate list opens when done",
"Menganalisis video contoh, sekitar 2–4 menit; daftar kandidat terbuka setelah selesai"
],
"開始產生 GPU 訓練包": [
"Start building GPU training package",
"Mulai buat paket latih GPU"
],
"開始訓練": [
"Start training",
"Mulai latih"
],
"開始訓練（約 20～60 分鐘）": [
"Start training (about 20～60 min)",
"Mulai latih (sekitar 20～60 menit)"
],
"開始訓練，進度在右下角；訓練中可以離開這個頁面，回來再看。訓練完會自動排好步驟。": [
"Training started; progress is at the bottom right. You can leave this page during training and come back later. Steps are arranged automatically when done.",
"Latih dimulai, progres ada di kanan bawah. Selama latih boleh tinggalkan halaman ini dan kembali nanti. Setelah selesai, langkah otomatis tersusun."
],
"開始錄製": [
"Start recording",
"Mulai rekam"
],
"開著": [
"Open",
"Terbuka"
],
"關閉": [
"Close",
"Tutup"
],
"離下一段太近，放不下新的一段。": [
"Too close to the next segment, no room for a new segment.",
"Terlalu dekat dengan segmen berikutnya, tidak muat segmen baru."
],
"離線驗證（{0}）…": [
"Offline validation ({0})…",
"Verifikasi offline ({0})…"
],
"需要注意": [
"Needs attention",
"Perlu perhatian"
],
"鞋": [
"Shoe",
"Sepatu"
],
"音量": [
"Volume",
"Volume"
],
"順序": [
"Order",
"Urutan"
],
"順序照示範影片第一次出現的先後（包裝設定頁的段落）。要改順序：到「包裝設定（訓練）」調段落再按「前往監控」。停留秒數、必要改了直接存。": [
"The order follows when each item first appears in the demo video (segments on the Packing setup page). To change the order: go to \"Packing setup (training)\", adjust the segments, then press \"Go to monitor\". Hold seconds and Required are saved as soon as you change them.",
"Urutan mengikuti kapan barang pertama kali muncul di video contoh (segmen di halaman Pengaturan kemas). Untuk ubah urutan: buka \"Pengaturan kemas (latih)\", atur segmen, lalu tekan \"Ke pantau\". Detik tahan dan Wajib langsung tersimpan saat diubah."
],
"順序照示範影片第一次出現的先後（標記物品的段落）。要改順序：到「標記物品」調段落再按「前往監控」。停留秒數、必要改了直接存。": [
"The order follows when each item first appears in the demo video (the Label items segments). To change the order: go to \"Label items\", adjust the segments, then press \"Go to monitor\". Hold seconds and Required are saved as soon as you change them.",
"Urutan mengikuti kapan barang pertama kali muncul di video contoh (segmen Tandai barang). Untuk ubah urutan: buka \"Tandai barang\", atur segmen, lalu tekan \"Ke pantau\". Detik tahan dan Wajib langsung tersimpan saat diubah."
],
"預覽（分析步驟、找出要補框的地方）": [
"Preview (analyze steps, find where boxes are needed)",
"Pratinjau (analisis langkah, cari bagian yang perlu ditambah kotak)"
],
"預覽（逐段看畫面、刪錯框）": [
"Preview (view each segment, delete wrong boxes)",
"Pratinjau (lihat tiap segmen, hapus kotak yang salah)"
],
"顯示卡記憶體不足（CUDA out of memory）：這台的記憶體被其他程式（例如訓練或 vLLM）佔滿了，請先關掉或等它們跑完再按開始": [
"Graphics card out of memory (CUDA out of memory): other programs on this PC (e.g. training or vLLM) are using it all; close them or wait for them to finish, then press Start",
"Memori kartu grafis habis (CUDA out of memory): program lain di PC ini (mis. pelatihan atau vLLM) memakai semuanya; tutup atau tunggu selesai, lalu tekan Mulai"
],
"顯示整支影片（快速鍵 \\）": [
"Show whole video (shortcut \\)",
"Tampilkan seluruh video (shortcut \\)"
],
"驗證判錯": [
"Check errors",
"Cek salah"
],
"驗證日期": [
"Check date",
"Tanggal cek"
],
"驗證沒過，保留舊模型（新模型存成 candidate.pt）": [
"Validation failed, keeping old model (new model saved as candidate.pt)",
"Verifikasi gagal, model lama tetap dipakai (model baru disimpan sebagai candidate.pt)"
],
"驗證漏看：": [
"Validation missed: ",
"Terlewat saat verifikasi: "
],
"驗證用": [
"For checking",
"Untuk cek"
],
"驗證結果": [
"Check result",
"Hasil cek"
],
"驗證結果只能是 {0}": [
"Validation result can only be {0}",
"Hasil validasi hanya boleh {0}"
],
"驗證：": [
"　Verify: ",
"　Verifikasi: "
],
"點了選今天要做的型體和它要用的模型": [
"Click to choose today's style and its model",
"Klik untuk pilih artikel hari ini dan modelnya"
],
"點我換": [
"Click to change",
"Klik untuk ganti"
],
"點模型就切換（同型體有幾個地區就幾個），模型載入約 10～30 秒": [
"Click a model to switch (one per region of the style); model loads in about 10–30 s",
"Klik model untuk pindah (satu per wilayah artikel); model dimuat sekitar 10–30 detik"
],
"（Ctrl＋Z 可以復原）": [
"(Ctrl+Z to undo)",
"(Ctrl+Z untuk batalkan)"
],
"（{0} 段未存）": [
"({0} segments unsaved)",
"({0} segmen belum disimpan)"
],
"（{0}，清單裡沒有）": [
"({0}, not in the list)",
"({0}, tidak ada di daftar)"
],
"（不接）": [
"(not linked)",
"(tidak disambung)"
],
"（停用）": [
" (disabled)",
" (nonaktif)"
],
"（右邊點一個名稱）": [
"(click a name on the right)",
"(klik satu nama di kanan)"
],
"（影片換過了，請重新分析）": [
" (the video changed, please analyse again)",
" (video sudah diganti, analisis ulang)"
],
"（待刪 {0}）": [
"(to delete {0})",
"(akan dihapus {0})"
],
"（把整套動作完整做幾遍）": [
"(do the full set of actions a few times)",
"(lakukan semua gerakan lengkap beberapa kali)"
],
"（有密碼）": [
"(password set)",
"(ada password)"
],
"（未填）": [
"(not filled)",
"(belum diisi)"
],
"（未設定）": [
" (not set)",
" (belum diatur)"
],
"（沒有任何動作分段）": [
"(no action segments)",
"(tidak ada segmen gerakan)"
],
"（沒有型體）": [
"(No style)",
"(Tidak ada artikel)"
],
"（沒有密碼：同資料夾放 web_password.txt 就會要求輸入）": [
"(no password: put web_password.txt in the same folder to require one)",
"(tanpa password: taruh web_password.txt di folder yang sama untuk mewajibkan password)"
],
"（沒有影片）": [
"(no video)",
"(tidak ada video)"
],
"（沒看到任何物品）": [
"(No items seen)",
"(Tidak ada barang terlihat)"
],
"（無）": [
"(None)",
"(Tidak ada)"
],
"（補傳了 {0}）": [
" (resent {0})",
" (kirim ulang {0})"
],
"（要先在 buzzer.json 設指令）": [
" (set the commands in buzzer.json first)",
" (atur perintah di buzzer.json dulu)"
],
"（試跑）": [
" (trial run)",
" (uji coba)"
],
"（請確認網址、帳號密碼與網路）": [
"(check the URL, username/password and network)",
"(cek URL, username/password, dan jaringan)"
],
"（連同參考的模型：{0}）": [
" (with referenced model: {0})",
" (beserta model acuan: {0})"
],
"（選專案）": [
"(choose project)",
"(pilih proyek)"
],
"（選配）": [
"(Optional)",
"(Opsional)"
],
"（還有 {0} 個沒取名）": [
" ({0} still unnamed)",
" ({0} belum diberi nama)"
],
"（還沒選名稱）": [
"(no name selected yet)",
"(belum pilih nama)"
],
"（點上面一列）": [
" (click a row above)",
" (klik baris di atas)"
],
"，{0} 秒後也會自動解除": [
", will also clear automatically in {0} s",
", juga akan hilang otomatis dalam {0} detik"
],
"，不然監控時看到的東西大小跟訓練時不一樣": [
", otherwise items will look a different size in monitoring than in training",
", kalau tidak, ukuran barang saat dipantau beda dengan saat dilatih"
],
"，共 {0} 段（另加 {1} 格反例）。可以檢查、刪掉不對的段落，再按訓練。": [
", {0} segments in total (plus {1} negative frames). Check and delete wrong segments, then train.",
", total {0} segmen (ditambah {1} bingkai negatif). Periksa dan hapus segmen yang salah, lalu latih."
],
"，共用硬碟有新版": [
", shared drive has a newer version",
", drive bersama punya versi baru"
],
"，合成配色：{0}": [
", synthetic colors: {0}",
", warna sintetis: {0}"
],
"，新框的才會被認得": [
", only newly drawn boxes will be recognized",
", hanya kotak baru yang akan dikenali"
],
"，本機改過還沒上傳": [
", changed locally but not uploaded yet",
", diubah di komputer ini tapi belum diunggah"
],
"，正在重新載入": [
", reloading",
", memuat ulang"
],
"，而且要疊在「{0}」上": [
", and it must be on top of \"{0}\"",
", dan harus berada di atas \"{0}\""
],
"／超時 {0}": [
" / overtime {0}",
" / lewat waktu {0}"
],
"：到「包裝設定（訓練）」按「重新訓練」": [
": go to \"Packing setup (training)\" and press \"Retrain\"",
": buka \"Pengaturan kemas (latih)\" lalu tekan \"Latih ulang\""
],
"：到「標記物品」按「重新訓練」": [
": go to \"Label items\" and press \"Retrain\"",
": buka \"Tandai barang\" lalu tekan \"Latih ulang\""
],
"：訓練 {0} 段、驗證 {1} 段": [
": train {0} segments, check {1} segments",
": latih {0} segmen, cek {1} segmen"
],
"；待刪 {0} 格": [
"; {0} frames to delete",
"; {0} frame akan dihapus"
],
"；舊版框選 {0} 格不在時間軸上，訓練時一樣會用到": [
"; {0} frames boxed in the old version are not on the timeline but will still be used in training",
"; {0} frame kotak versi lama tidak ada di timeline, tapi tetap dipakai saat latih"
],
"；還有 {0} 沒傳": [
"; {0} still not sent",
"; {0} masih belum terkirim"
],
"🔇 點一下啟用警報聲": [
"🔇 Click to enable alarm sound",
"🔇 Klik untuk mengaktifkan bunyi alarm"
],
"🔕 靜音": [
"🔕 Mute",
"🔕 Bisukan"
]
};
