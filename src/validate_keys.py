"""
KT7 - Kiem tra tinh toan ven khoa chinh va khoa ngoai (PK / FK Integrity)
Fashion_DW_Project

Pham vi: 11 bang nghiep vu chinh trong data/raw/
Ngoai pham vi: sales.csv, web_traffic.csv, sample_submission.csv,
               submission_idea42_alphaequal.csv

Nguyen tac:
  - Chi kiem tra, khong sua doi du lieu nguon.
  - Du lieu trong data/raw/ duoc giu nguyen 100%.
  - Ket qua xuat ra: docs/key_validation_report.csv
                     docs/key_validation_issues.csv

Chay doc lap:
  python src/validate_keys.py
"""

import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR  = BASE_DIR / "data" / "raw"
DOCS_DIR = BASE_DIR / "docs"
DOCS_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# 1. DOC DU LIEU NGUON
# ============================================================
TABLES = [
    "customers", "geography", "inventory", "order_items", "orders",
    "payments", "products", "promotions", "returns", "reviews", "shipments"
]
print("Dang doc du lieu...")
dfs = {t: pd.read_csv(RAW_DIR / f"{t}.csv", low_memory=False) for t in TABLES}

customers   = dfs["customers"]
geography   = dfs["geography"]
inventory   = dfs["inventory"]
order_items = dfs["order_items"]
orders      = dfs["orders"]
payments    = dfs["payments"]
products    = dfs["products"]
promotions  = dfs["promotions"]
returns     = dfs["returns"]
reviews     = dfs["reviews"]
shipments   = dfs["shipments"]

print("Doc xong. Bat dau kiem tra KT7...\n")

ket_qua = []      # Bang tong hop 78 tieu chi
issues_list = []  # Danh sach ban ghi co van de can xem xet
SEP = "=" * 65

def log(ma, bang, loai_kiem_tra, cot, so_van_de, tong, trang_thai, ghi_chu):
    """Ghi nhan ket qua kiem tra vao danh sach tong hop."""
    ket_qua.append({
        "Ma_KT":         ma,
        "Bang":          bang,
        "Loai_kiem_tra": loai_kiem_tra,
        "Cot":           cot,
        "So_van_de":     so_van_de,
        "Tong_ban_ghi":  tong,
        "Ty_le_%":       round(so_van_de / tong * 100, 4) if tong > 0 else 0,
        "Trang_thai":    trang_thai,
        "Ghi_chu":       ghi_chu,
    })

def log_issues(bang, loai, cot, df_sub):
    """Ghi nhan chi tiet cac ban ghi co van de hoac can xem xet."""
    if len(df_sub) > 0:
        tmp = df_sub.copy()
        tmp["_bang"]        = bang
        tmp["_loai_van_de"] = loai
        tmp["_cot"]         = cot
        issues_list.append(tmp)

# ============================================================
# PHAN 1: KIEM TRA KHOA CHINH (Primary Key)
# ============================================================
print(SEP)
print("PHAN 1: KIEM TRA KHOA CHINH")
print(SEP)

def check_pk(ma, bang, cot, note_null="Khoa chinh bat buoc", note_dup="Khoa chinh bat buoc"):
    """Ham dung chung kiem tra khoa chinh don: kiem tra NULL va Duplicate."""
    df = dfs[bang]
    tong = len(df)
    null_ck = df[cot].isna().sum()
    dup_ck  = df.duplicated(subset=[cot]).sum()
    status  = "DAT" if (null_ck == 0 and dup_ck == 0) else "KHONG_DAT"
    print(f"[{ma}] {bang}.{cot}  NULL={null_ck}  DUP={dup_ck}  => {status}")
    log(ma, bang, "PK_NULL", cot, null_ck, tong,
        "DAT" if null_ck == 0 else "KHONG_DAT", note_null)
    log(ma, bang, "PK_DUP", cot, dup_ck, tong,
        "DAT" if dup_ck == 0 else "KHONG_DAT", note_dup)
    if dup_ck > 0:
        log_issues(bang, "PK_DUP", cot, df[df.duplicated(subset=[cot], keep=False)])

# 1.1 customers.customer_id
check_pk("1.1", "customers", "customer_id")

# 1.2 geography.zip (zip co the trung thanh pho: dung khoa ghep (zip, city))
tong_geo = len(geography)
null_geo = geography["zip"].isna().sum()
dup_geo  = geography.duplicated(subset=["zip"]).sum()
dup_geo_city = geography.duplicated(subset=["zip", "city"]).sum()
status_geo = "DAT" if (null_geo == 0 and dup_geo_city == 0) else "KHONG_DAT"
note_geo = "Khoa ghep (zip, city) duoc dung neu zip trung" if dup_geo > 0 else "zip don la duy nhat"
print(f"[1.2] geography.zip  NULL={null_geo}  DUP_zip={dup_geo}  DUP_(zip,city)={dup_geo_city}  => {status_geo}")
log("1.2", "geography", "PK_NULL", "zip", null_geo, tong_geo,
    "DAT" if null_geo == 0 else "KHONG_DAT", "Khoa chinh hoac khoa ghep")
log("1.2", "geography", "PK_DUP", "zip", dup_geo, tong_geo,
    "NEEDS_REVIEW" if dup_geo > 0 else "DAT", note_geo)
log("1.2", "geography", "PK_DUP", "(zip,city)", dup_geo_city, tong_geo,
    "DAT" if dup_geo_city == 0 else "KHONG_DAT", "Khoa ghep (zip,city)")
if dup_geo > 0:
    log_issues("geography", "PK_DUP_zip", "zip",
               geography[geography.duplicated(subset=["zip"], keep=False)])

# 1.3 - 1.5 PK don
check_pk("1.3", "products",   "product_id")
check_pk("1.4", "promotions", "promo_id")
check_pk("1.5", "orders",     "order_id")

# 1.6 order_items: Khoa ghep (order_id, product_id, promo_id)
# Nghiep vu: 16 cap (order_id, product_id) trung nhung khac promo_id/gia => 32 dong can xem xet
tong_oi = len(order_items)
null_oi_oid = order_items["order_id"].isna().sum()
null_oi_pid = order_items["product_id"].isna().sum()
dup_2col    = order_items.duplicated(subset=["order_id", "product_id"]).sum()
dup_3col    = order_items.duplicated(subset=["order_id", "product_id", "promo_id"]).sum()
status_oi2  = "NEEDS_REVIEW" if dup_2col > 0 else "DAT"
status_oi3  = "DAT" if dup_3col == 0 else "KHONG_DAT"
print(f"[1.6] order_items: NULL order_id={null_oi_oid}  NULL product_id={null_oi_pid}")
print(f"      DUP (order_id,product_id)={dup_2col}  DUP (order_id,product_id,promo_id)={dup_3col}")
log("1.6", "order_items", "PK_NULL", "order_id", null_oi_oid, tong_oi,
    "DAT" if null_oi_oid == 0 else "KHONG_DAT", "Bat buoc, khoa ngoai den orders")
log("1.6", "order_items", "PK_NULL", "product_id", null_oi_pid, tong_oi,
    "DAT" if null_oi_pid == 0 else "KHONG_DAT", "Bat buoc, khoa ngoai den products")
log("1.6", "order_items", "PK_DUP", "(order_id,product_id)", dup_2col, tong_oi,
    status_oi2, "Mot don co the mua 2 dong san pham giong nhau (khac promo/gia)")
log("1.6", "order_items", "PK_DUP", "(order_id,product_id,promo_id)", dup_3col, tong_oi,
    status_oi3, "Khoa ghep 3 cot sau khi phan tich nghiep vu")
if dup_2col > 0:
    log_issues("order_items", "PK_DUP_(order_id,product_id)", "(order_id,product_id)",
               order_items[order_items.duplicated(subset=["order_id", "product_id"], keep=False)])

# 1.7 - 1.10 PK don / quan he 1-1
check_pk("1.7",  "payments",  "order_id",   note_null="1-1 voi orders",                       note_dup="Moi don hang chi co 1 thanh toan")
check_pk("1.8",  "shipments", "order_id",   note_null="Moi don hang 1 van chuyen (xac nhan)", note_dup="1-1 voi orders")
check_pk("1.9",  "returns",   "return_id")
check_pk("1.10", "reviews",   "review_id")

# 1.11 inventory: Khoa ghep (snapshot_date, product_id)
tong_inv = len(inventory)
null_inv_date = inventory["snapshot_date"].isna().sum()
null_inv_pid  = inventory["product_id"].isna().sum()
dup_inv       = inventory.duplicated(subset=["snapshot_date", "product_id"]).sum()
status_inv    = "DAT" if (null_inv_date == 0 and null_inv_pid == 0 and dup_inv == 0) else "KHONG_DAT"
print(f"[1.11] inventory (snapshot_date,product_id)  NULL_date={null_inv_date}  NULL_pid={null_inv_pid}  DUP={dup_inv}  => {status_inv}")
log("1.11", "inventory", "PK_NULL", "snapshot_date", null_inv_date, tong_inv,
    "DAT" if null_inv_date == 0 else "KHONG_DAT", "Phan cua khoa ghep")
log("1.11", "inventory", "PK_NULL", "product_id", null_inv_pid, tong_inv,
    "DAT" if null_inv_pid == 0 else "KHONG_DAT", "Phan cua khoa ghep")
log("1.11", "inventory", "PK_DUP", "(snapshot_date,product_id)", dup_inv, tong_inv,
    "DAT" if dup_inv == 0 else "KHONG_DAT", "Khoa ghep chinh")

# ============================================================
# PHAN 2: KIEM TRA KHOA NGOAI (Foreign Key)
# ============================================================
print(f"\n{SEP}")
print("PHAN 2: KIEM TRA KHOA NGOAI")
print(SEP)

valid_keys = {
    "customers.customer_id": set(customers["customer_id"].dropna()),
    "geography.zip":         set(geography["zip"].dropna()),
    "products.product_id":   set(products["product_id"].dropna()),
    "promotions.promo_id":   set(promotions["promo_id"].dropna()),
    "orders.order_id":       set(orders["order_id"].dropna()),
}
valid_order_item_keys = set(zip(order_items["order_id"], order_items["product_id"]))

def check_fk(bang_con, cot_con, bang_cha, cot_cha, cho_phep_null=True):
    """Ham dung chung kiem tra khoa ngoai: kiem tra NULL va orphan FK."""
    df_con = dfs[bang_con]
    valid_set = valid_keys[f"{bang_cha}.{cot_cha}"]
    tong = len(df_con)
    null_cnt = df_con[cot_con].isna().sum()
    co_gia_tri = df_con[df_con[cot_con].notna()]
    orphan_mask = ~co_gia_tri[cot_con].isin(valid_set)
    orphan_cnt = orphan_mask.sum()
    tong_kt = len(co_gia_tri)

    null_status = "KHONG_DAT" if (null_cnt > 0 and not cho_phep_null) else "DAT"
    fk_status = "DAT" if orphan_cnt == 0 else "KHONG_DAT"

    print(f"  FK {bang_con}.{cot_con} -> {bang_cha}.{cot_cha}: "
          f"NULL={null_cnt}  Orphan={orphan_cnt}/{tong_kt}  => NULL:{null_status} / FK:{fk_status}")

    log("FK", bang_con, "FK_NULL", cot_con, null_cnt, tong,
        null_status, f"FK -> {bang_cha}.{cot_cha}" + (" (bat buoc)" if not cho_phep_null else " (tuy chon)"))
    log("FK", bang_con, "FK_ORPHAN", cot_con, orphan_cnt, tong_kt,
        fk_status, f"FK -> {bang_cha}.{cot_cha}")

    if orphan_cnt > 0:
        orphan_rows = co_gia_tri[orphan_mask][[cot_con]].drop_duplicates().copy()
        log_issues(bang_con, f"FK_ORPHAN_{cot_con}", cot_con, orphan_rows)

    return null_cnt, orphan_cnt

def check_parent_completeness(bang_con, cot_con, bang_cha, cot_cha,
                              status_on_missing="KHONG_DAT", note=""):
    """Kiem tra don hang cha bi thieu trong bang con (1-1 hoac theo doi trang thai)."""
    parent_ids = valid_keys[f"{bang_cha}.{cot_cha}"]
    child_ids  = set(dfs[bang_con][cot_con].dropna())
    missing    = parent_ids - child_ids
    pct        = len(missing) / len(parent_ids) * 100 if len(parent_ids) > 0 else 0
    status     = "DAT" if len(missing) == 0 else status_on_missing

    if pct > 0:
        print(f"  {bang_cha} khong co trong {bang_con}: {len(missing)} ({pct:.2f}%)")
    else:
        print(f"  {bang_cha} khong co trong {bang_con}: {len(missing)}")

    log("FK", bang_con, "FK_MISSING_PARENT", cot_con, len(missing), len(parent_ids), status, note)
    return len(missing)

def check_composite_fk(bang_con, cols, bang_cha, note):
    """Kiem tra toan ven khoa ngoai ghep (order_id, product_id) doi chieu order_items."""
    child_keys = set(zip(dfs[bang_con][cols[0]], dfs[bang_con][cols[1]]))
    col_str = f"({cols[0]},{cols[1]})"
    orphan_keys = child_keys - valid_order_item_keys
    status = "DAT" if len(orphan_keys) == 0 else "KHONG_DAT"
    print(f"  {bang_con} {col_str} khong co trong {bang_cha}: {len(orphan_keys)}")
    log("FK", bang_con, "FK_COMPOSITE_ORPHAN", col_str, len(orphan_keys), len(dfs[bang_con]), status, note)
    return len(orphan_keys)

# [orders FK]
print("\n[orders FK]")
check_fk("orders", "customer_id", "customers", "customer_id", cho_phep_null=False)
check_fk("orders", "zip",         "geography", "zip",         cho_phep_null=False)

# [order_items FK]
print("\n[order_items FK]")
check_fk("order_items", "order_id",   "orders",     "order_id",   cho_phep_null=False)
check_fk("order_items", "product_id", "products",   "product_id", cho_phep_null=False)
check_fk("order_items", "promo_id",   "promotions", "promo_id",   cho_phep_null=True)
check_fk("order_items", "promo_id_2", "promotions", "promo_id",   cho_phep_null=True)

# [payments FK]
print("\n[payments FK]")
check_fk("payments", "order_id", "orders", "order_id", cho_phep_null=False)
check_parent_completeness("payments", "order_id", "orders", "order_id",
                          status_on_missing="DAT", note="Moi don phai co payment (1-1)")

# [shipments FK]
print("\n[shipments FK]")
check_fk("shipments", "order_id", "orders", "order_id", cho_phep_null=False)
check_parent_completeness("shipments", "order_id", "orders", "order_id",
                          status_on_missing="NEEDS_REVIEW",
                          note="Don chua van chuyen co the la don huy/cho xu ly")

# [returns FK]
print("\n[returns FK]")
check_fk("returns", "order_id",   "orders",   "order_id",   cho_phep_null=False)
check_fk("returns", "product_id", "products", "product_id", cho_phep_null=False)
check_composite_fk("returns", ("order_id", "product_id"), "order_items",
                   note="Phai ton tai dong san pham trong order_items moi tra hang duoc")

# [reviews FK]
print("\n[reviews FK]")
check_fk("reviews", "order_id",    "orders",    "order_id",    cho_phep_null=False)
check_fk("reviews", "product_id",  "products",  "product_id",  cho_phep_null=False)
check_fk("reviews", "customer_id", "customers", "customer_id", cho_phep_null=False)
check_composite_fk("reviews", ("order_id", "product_id"), "order_items",
                   note="Phai mua san pham moi duoc review")

# [inventory FK]
print("\n[inventory FK]")
check_fk("inventory", "product_id", "products", "product_id", cho_phep_null=False)

# [customers FK]
print("\n[customers FK]")
check_fk("customers", "zip", "geography", "zip", cho_phep_null=False)

# ============================================================
# PHAN 3: KIEU DU LIEU GIUA CAC KHOA LIEN KET
# ============================================================
print(f"\n{SEP}")
print("PHAN 3: KIEM TRA KIEU DU LIEU KHOA LIEN KET")
print(SEP)

DTYPE_CHECKS = [
    ("orders",      "customer_id", "customers",  "customer_id"),
    ("orders",      "zip",         "geography",  "zip"),
    ("order_items", "order_id",    "orders",     "order_id"),
    ("order_items", "product_id",  "products",   "product_id"),
    ("order_items", "promo_id",    "promotions", "promo_id"),
    ("payments",    "order_id",    "orders",     "order_id"),
    ("shipments",   "order_id",    "orders",     "order_id"),
    ("returns",     "order_id",    "orders",     "order_id"),
    ("returns",     "product_id",  "products",   "product_id"),
    ("reviews",     "order_id",    "orders",     "order_id"),
    ("reviews",     "product_id",  "products",   "product_id"),
    ("reviews",     "customer_id", "customers",  "customer_id"),
    ("inventory",   "product_id",  "products",   "product_id"),
    ("customers",   "zip",         "geography",  "zip"),
]

for b_con, c_con, b_cha, c_cha in DTYPE_CHECKS:
    dt_con = dfs[b_con][c_con].dtype
    dt_cha = dfs[b_cha][c_cha].dtype
    khop = (str(dt_con) == str(dt_cha))
    status_dt = "DAT" if khop else "NEEDS_REVIEW"
    print(f"  {b_con}.{c_con} ({dt_con}) -> {b_cha}.{c_cha} ({dt_cha})  => {status_dt}")
    log("3", b_con, "DTYPE_MISMATCH", c_con, 0 if khop else 1, 1, status_dt, f"{dt_con} vs {dt_cha}")

# ============================================================
# PHAN 4: FILES NGOAI PHAM VI KIEM TRA QUAN HE
# ============================================================
print(f"\n{SEP}")
print("PHAN 4: FILES NGOAI PHAM VI KIEM TRA QUAN HE")
print(SEP)

NGOAI_PHAM_VI = ["sales.csv", "web_traffic.csv", "sample_submission.csv", "submission_idea42_alphaequal.csv"]
for f in NGOAI_PHAM_VI:
    print(f"  {f}: Khong ap dung kiem tra FK - file tong hop / du bao (NEEDS_REVIEW tuong lai)")
    log("4", f.replace(".csv", ""), "SCOPE_EXCLUDED", "N/A", 0, 0, "NEEDS_REVIEW",
        "File tong hop / du bao, chua xac dinh quan he voi bang nghiep vu")

# ============================================================
# XUAT KET QUA RA FILE
# ============================================================
print(f"\n{SEP}")
print("XUAT KET QUA RA FILE")
print(SEP)

df_report = pd.DataFrame(ket_qua)
df_report.to_csv(DOCS_DIR / "key_validation_report.csv", index=False, encoding="utf-8-sig")
print(f"[OK] Luu bao cao: docs/key_validation_report.csv ({len(df_report)} dong)")

if issues_list:
    df_issues = pd.concat(issues_list, ignore_index=True)
    df_issues.to_csv(DOCS_DIR / "key_validation_issues.csv", index=False, encoding="utf-8-sig")
    print(f"[OK] Luu danh sach van de: docs/key_validation_issues.csv ({len(df_issues)} dong)")
else:
    pd.DataFrame().to_csv(DOCS_DIR / "key_validation_issues.csv", index=False, encoding="utf-8-sig")
    print("[OK] Khong co ban ghi van de nao. File rong duoc tao: docs/key_validation_issues.csv")

# ============================================================
# TONG KET
# ============================================================
print(f"\n{SEP}")
print("TONG KET KT7")
print(SEP)

dem = df_report["Trang_thai"].value_counts()
print(df_report[["Ma_KT", "Bang", "Loai_kiem_tra", "Cot", "So_van_de", "Tong_ban_ghi", "Ty_le_%", "Trang_thai"]].to_string(index=False))
print()
print("SO LUONG KIEM TRA THEO TRANG THAI:")
print(dem.to_string())
print("\n[GHI CHU] Day chi la buoc KIEM TRA. Chua thuc hien lam sach hoac sua du lieu.")
