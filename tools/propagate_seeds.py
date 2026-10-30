"""跨輪次自動標註工具：
將使用者在第 1 輪人工標記的物品種子，透過樣板比對與色彩檢驗，自動在第 2 輪與第 3 輪尋找對應位置並建立標記。

用法：
    python tools/propagate_seeds.py <專案名稱> [--track-sec 2.0]
"""
import argparse
import os
import sys
import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from project_store import load_project
from item_recognizer import ItemSeeds, track_seed, _gray
from core_detector import roi_similarity


def propagate_project(project_name: str, track_sec: float = 2.0) -> dict:
    project = load_project(project_name)
    seeds = ItemSeeds(project.dir_path)
    
    # 取得第 1 輪的手動標記
    r1_manuals = [s for s in seeds.seeds if not s.auto and s.frame <= 1200]
    if not r1_manuals:
        raise ValueError("在第 1 輪（格數 <= 1200）找不到手動標記的種子")
    
    cap = cv2.VideoCapture(project.video_path)
    fps = project.fps or 30.0
    
    # 輪次搜尋區間（第 2 輪約 1250..1600 格，第 3 輪約 1650..2020 格）
    target_windows = [
        ("第 2 輪", 1250, 1600),
        ("第 3 輪", 1650, 2020),
    ]
    
    # 桌面搜尋範圍（如果專案有設桌面範圍）
    desk = seeds.region or [0, 0, int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))]
    dx, dy, dw, dh = desk
    
    added_manuals = []
    total_auto = 0
    
    for m in r1_manuals:
        mx, my, mw, mh = m.rect
        cap.set(cv2.CAP_PROP_POS_FRAMES, m.frame)
        ok, fr0 = cap.read()
        if not ok:
            continue
        
        tpl_bgr = fr0[my:my+mh, mx:mx+mw]
        tpl_gray = _gray(tpl_bgr)
        if tpl_gray.size == 0 or tpl_gray.shape[0] < 8 or tpl_gray.shape[1] < 8:
            continue
            
        for round_name, start_f, end_f in target_windows:
            # 檢查是否該輪已經有該物品的手框
            existing = [s for s in seeds.seeds if s.name == m.name and start_f <= s.frame <= end_f and not s.auto]
            if existing:
                continue
                
            best_score = -1.0
            best_f = -1
            best_rect = None
            
            # 每 3 格搜尋一次
            for f in range(start_f, end_f, 3):
                cap.set(cv2.CAP_PROP_POS_FRAMES, f)
                ok, fr = cap.read()
                if not ok:
                    break
                
                # 在桌面區域內比對
                crop_desk = fr[dy:dy+dh, dx:dx+dw]
                crop_gray = _gray(crop_desk)
                if crop_gray.shape[0] < mh or crop_gray.shape[1] < mw:
                    continue
                    
                res = cv2.matchTemplate(crop_gray, tpl_gray, cv2.TM_CCOEFF_NORMED)
                _, max_v, _, max_l = cv2.minMaxLoc(res)
                if max_v < 0.35:
                    continue
                    
                rx = max_l[0] + dx
                ry = max_l[1] + dy
                crop_cand = fr[ry:ry+mh, rx:rx+mw]
                color_sim = roi_similarity(tpl_bgr, crop_cand)
                
                score = max_v * 0.7 + color_sim * 0.3
                if score > best_score and color_sim >= 0.35 and max_v >= 0.40:
                    best_score = score
                    best_f = f
                    best_rect = (rx, ry, mw, mh)
                    
            if best_f > 0 and best_rect is not None:
                auto = track_seed(project.video_path, best_f, best_rect, window_sec=track_sec, fps=fps) if track_sec > 0 else []
                seeds.add_seed(m.name, best_f, best_rect, auto)
                added_manuals.append({"name": m.name, "round": round_name, "frame": best_f, "rect": list(best_rect), "score": round(best_score, 2)})
                total_auto += len(auto)
                print(f"[{m.name}] 成功推廣至 {round_name}（第 {best_f} 格，相似度 {best_score:.2f}，自動追出 {len(auto)} 格）")
                
    cap.release()
    seeds.save()
    return {"added_manuals": added_manuals, "total_auto": total_auto}


def main():
    parser = argparse.ArgumentParser(description="自動將第 1 輪標記內容推廣至第 2、3 輪")
    parser.add_argument("project", help="專案名稱，例如 310237")
    parser.add_argument("--track-sec", type=float, default=2.0, help="自動前後追蹤秒數（預設 2.0）")
    args = parser.parse_args()
    
    print(f"開始分析專案「{args.project}」第 1 輪標記並向後傳播...")
    res = propagate_project(args.project, track_sec=args.track_sec)
    print(f"傳播完成！共新增 {len(res['added_manuals'])} 個跨輪手框，自動延伸 {res['total_auto']} 格。")


if __name__ == "__main__":
    main()
