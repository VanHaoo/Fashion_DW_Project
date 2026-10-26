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
# DOC DU LIEU
# ============================================================
print("Dang doc du lieu...")
customers  = pd.read_csv(RAW_DIR / "customers.csv",   low_memory=False)
geography  = pd.read_csv(RAW_DIR / "geography.csv",    low_memory=False)
inventory  = pd.read_csv(RAW_DIR / "inventory.csv",    low_memory=False)
order_items= pd.read_csv(RAW_DIR / "order_items.csv",  low_memory=False)
orders     = pd.read_csv(RAW_DIR / "orders.csv",       low_memory=False)
payments   = pd.read_csv(RAW_DIR / "payments.csv",     low_memory=False)
products   = pd.read_csv(RAW_DIR / "products.csv",     low_memory=False)
promotions = pd.read_csv(RAW_DIR / "promotions.csv",   low_memory=False)
returns    = pd.read_csv(RAW_DIR / "returns.csv",      low_memory=False)
reviews    = pd.read_csv(RAW_DIR / "reviews.csv",      low_memory=False)
shipments  = pd.read_csv(RAW_DIR / "shipments.csv",    low_memory=False)

# File du bao / khong co quan he nghiep vu => bo qua kiem tra FK
# sales.csv, web_traffic.csv, sample_submission.csv, submission_idea42_alphaequal.csv

print("Doc xong. Bat dau kiem tra KT7...\n")

ket_qua   = []   # bang tong hop
issues_list = []  # danh sach ban ghi co van de

SEP = "=" * 65

def log(ma, bang, loai_kiem_tra, cot, so_van_de, tong, trang_thai, ghi_chu):
    ket_qua.append({
        "Ma_KT":          ma,
        "Bang":           bang,
        "Loai_kiem_tra":  loai_kiem_tra,
        "Cot":            cot,
        "So_van_de":      so_van_de,
        "Tong_ban_ghi":   tong,
        "Ty_le_%":        round(so_van_de / tong * 100, 4) if tong > 0 else 0,
        "Trang_thai":     trang_thai,
        "Ghi_chu":        ghi_chu,
    })

def log_issues(bang, loai, cot, df_sub):
    if len(df_sub) > 0:
        tmp = df_sub.copy()
        tmp["_bang"]       = bang
        tmp["_loai_van_de"]= loai
        tmp["_cot"]        = cot
        issues_list.append(tmp)

# ============================================================
# PHAN 1: KHOA CHINH (Primary Key)
# ============================================================
print(SEP)
print("PHAN 1: KIEM TRA KHOA CHINH")
print(SEP)

# -------------------------------------------------------
# 1.1 customers.customer_id
# -------------------------------------------------------
tong = len(customers)
null_ck = customers["customer_id"].isna().sum()
dup_ck  = customers.duplicated(subset=["customer_id"]).sum()
status1a = "DAT" if (null_ck == 0 and dup_ck == 0) else "KHONG_DAT"
print(f"[1.1] customers.customer_id  NULL={null_ck}  DUP={dup_ck}  => {status1a}")
log("1.1","customers","PK_NULL","customer_id",null_ck,tong,
    "DAT" if null_ck==0 else "KHONG_DAT","Khoa chinh bat buoc")
log("1.1","customers","PK_DUP","customer_id",dup_ck,tong,
    "DAT" if dup_ck==0 else "KHONG_DAT","Khoa chinh bat buoc")
if dup_ck > 0:
    log_issues("customers","PK_DUP","customer_id",
               customers[customers.duplicated(subset=["customer_id"],keep=False)])

# -------------------------------------------------------
# 1.2 geography.zip  (zip co the khong la duy nhat: nhieu city cung zip?)
# -------------------------------------------------------
tong = len(geography)
null_geo = geography["zip"].isna().sum()
dup_geo  = geography.duplicated(subset=["zip"]).sum()
dup_geo_city = geography.duplicated(subset=["zip","city"]).sum()
status_geo = "DAT" if (null_geo==0 and dup_geo_city==0) else "KHONG_DAT"
note_geo = "Khoa ghep (zip, city) duoc dung neu zip trung" if dup_geo > 0 else "zip don la duy nhat"
print(f"[1.2] geography.zip  NULL={null_geo}  DUP_zip={dup_geo}  DUP_(zip,city)={dup_geo_city}  => {status_geo}")
log("1.2","geography","PK_NULL","zip",null_geo,tong,
    "DAT" if null_geo==0 else "KHONG_DAT","Khoa chinh hoac khoa ghep")
log("1.2","geography","PK_DUP","zip",dup_geo,tong,
    "NEEDS_REVIEW" if dup_geo>0 else "DAT", note_geo)
log("1.2","geography","PK_DUP","(zip,city)",dup_geo_city,tong,
    "DAT" if dup_geo_city==0 else "KHONG_DAT","Khoa ghep (zip,city)")
if dup_geo > 0:
    log_issues("geography","PK_DUP_zip","zip",
               geography[geography.duplicated(subset=["zip"],keep=False)])

# -------------------------------------------------------
# 1.3 products.product_id
# -------------------------------------------------------
tong = len(products)
null_p = products["product_id"].isna().sum()
dup_p  = products.duplicated(subset=["product_id"]).sum()
status_p = "DAT" if (null_p==0 and dup_p==0) else "KHONG_DAT"
print(f"[1.3] products.product_id  NULL={null_p}  DUP={dup_p}  => {status_p}")
log("1.3","products","PK_NULL","product_id",null_p,tong,
    "DAT" if null_p==0 else "KHONG_DAT","Khoa chinh bat buoc")
log("1.3","products","PK_DUP","product_id",dup_p,tong,
    "DAT" if dup_p==0 else "KHONG_DAT","Khoa chinh bat buoc")

# -------------------------------------------------------
# 1.4 promotions.promo_id
# -------------------------------------------------------
tong = len(promotions)
null_pr = promotions["promo_id"].isna().sum()
dup_pr  = promotions.duplicated(subset=["promo_id"]).sum()
status_pr = "DAT" if (null_pr==0 and dup_pr==0) else "KHONG_DAT"
print(f"[1.4] promotions.promo_id  NULL={null_pr}  DUP={dup_pr}  => {status_pr}")
log("1.4","promotions","PK_NULL","promo_id",null_pr,tong,
    "DAT" if null_pr==0 else "KHONG_DAT","Khoa chinh bat buoc")
log("1.4","promotions","PK_DUP","promo_id",dup_pr,tong,
    "DAT" if dup_pr==0 else "KHONG_DAT","Khoa chinh bat buoc")

# -------------------------------------------------------
# 1.5 orders.order_id
# -------------------------------------------------------
tong = len(orders)
null_o = orders["order_id"].isna().sum()
dup_o  = orders.duplicated(subset=["order_id"]).sum()
status_o = "DAT" if (null_o==0 and dup_o==0) else "KHONG_DAT"
print(f"[1.5] orders.order_id  NULL={null_o}  DUP={dup_o}  => {status_o}")
log("1.5","orders","PK_NULL","order_id",null_o,tong,
    "DAT" if null_o==0 else "KHONG_DAT","Khoa chinh bat buoc")
log("1.5","orders","PK_DUP","order_id",dup_o,tong,
    "DAT" if dup_o==0 else "KHONG_DAT","Khoa chinh bat buoc")

# -------------------------------------------------------
# 1.6 order_items - khong co khoa don; khoa ghep (order_id, product_id, promo_id)
# Ghi chu: co 16 cap (order_id, product_id) bi trung, nhung khac promo_id
# -------------------------------------------------------
tong = len(order_items)
null_oi_oid = order_items["order_id"].isna().sum()
null_oi_pid = order_items["product_id"].isna().sum()
dup_2col    = order_items.duplicated(subset=["order_id","product_id"]).sum()
dup_3col    = order_items.duplicated(subset=["order_id","product_id","promo_id"]).sum()
status_oi2  = "NEEDS_REVIEW" if dup_2col > 0 else "DAT"
status_oi3  = "DAT" if dup_3col == 0 else "KHONG_DAT"
print(f"[1.6] order_items: NULL order_id={null_oi_oid}  NULL product_id={null_oi_pid}")
print(f"      DUP (order_id,product_id)={dup_2col}  DUP (order_id,product_id,promo_id)={dup_3col}")
log("1.6","order_items","PK_NULL","order_id",null_oi_oid,tong,
    "DAT" if null_oi_oid==0 else "KHONG_DAT","Bat buoc, khoa ngoai den orders")
log("1.6","order_items","PK_NULL","product_id",null_oi_pid,tong,
    "DAT" if null_oi_pid==0 else "KHONG_DAT","Bat buoc, khoa ngoai den products")
log("1.6","order_items","PK_DUP","(order_id,product_id)",dup_2col,tong,
    status_oi2,"Mot don co the mua 2 dong san pham giong nhau (khac promo/gia)")
log("1.6","order_items","PK_DUP","(order_id,product_id,promo_id)",dup_3col,tong,
    status_oi3,"Khoa ghep 3 cot sau khi phan tich nghiep vu")
if dup_2col > 0:
    log_issues("order_items","PK_DUP_(order_id,product_id)","(order_id,product_id)",
               order_items[order_items.duplicated(subset=["order_id","product_id"],keep=False)])

# -------------------------------------------------------
# 1.7 payments.order_id (1-1 voi orders)
# -------------------------------------------------------
tong = len(payments)
null_pay = payments["order_id"].isna().sum()
dup_pay  = payments.duplicated(subset=["order_id"]).sum()
status_pay = "DAT" if (null_pay==0 and dup_pay==0) else "KHONG_DAT"
print(f"[1.7] payments.order_id  NULL={null_pay}  DUP={dup_pay}  => {status_pay}")
log("1.7","payments","PK_NULL","order_id",null_pay,tong,
    "DAT" if null_pay==0 else "KHONG_DAT","1-1 voi orders")
log("1.7","payments","PK_DUP","order_id",dup_pay,tong,
    "DAT" if dup_pay==0 else "KHONG_DAT","Moi don hang chi co 1 thanh toan")

# -------------------------------------------------------
# 1.8 shipments.order_id (1-1 hoac 1-n?)
# -------------------------------------------------------
tong = len(shipments)
null_sh = shipments["order_id"].isna().sum()
dup_sh  = shipments.duplicated(subset=["order_id"]).sum()
status_sh = "DAT" if (null_sh==0 and dup_sh==0) else "KHONG_DAT"
print(f"[1.8] shipments.order_id  NULL={null_sh}  DUP={dup_sh}  => {status_sh}")
log("1.8","shipments","PK_NULL","order_id",null_sh,tong,
    "DAT" if null_sh==0 else "KHONG_DAT","Moi don hang 1 van chuyen (xac nhan)")
log("1.8","shipments","PK_DUP","order_id",dup_sh,tong,
    "DAT" if dup_sh==0 else "KHONG_DAT","1-1 voi orders")

# -------------------------------------------------------
# 1.9 returns.return_id
# -------------------------------------------------------
tong = len(returns)
null_r = returns["return_id"].isna().sum()
dup_r  = returns.duplicated(subset=["return_id"]).sum()
status_r = "DAT" if (null_r==0 and dup_r==0) else "KHONG_DAT"
print(f"[1.9] returns.return_id  NULL={null_r}  DUP={dup_r}  => {status_r}")
log("1.9","returns","PK_NULL","return_id",null_r,tong,
    "DAT" if null_r==0 else "KHONG_DAT","Khoa chinh bat buoc")
log("1.9","returns","PK_DUP","return_id",dup_r,tong,
    "DAT" if dup_r==0 else "KHONG_DAT","Khoa chinh bat buoc")

# -------------------------------------------------------
# 1.10 reviews.review_id
# -------------------------------------------------------
tong = len(reviews)
null_rv = reviews["review_id"].isna().sum()
dup_rv  = reviews.duplicated(subset=["review_id"]).sum()
status_rv = "DAT" if (null_rv==0 and dup_rv==0) else "KHONG_DAT"
print(f"[1.10] reviews.review_id  NULL={null_rv}  DUP={dup_rv}  => {status_rv}")
log("1.10","reviews","PK_NULL","review_id",null_rv,tong,
    "DAT" if null_rv==0 else "KHONG_DAT","Khoa chinh bat buoc")
log("1.10","reviews","PK_DUP","review_id",dup_rv,tong,
    "DAT" if dup_rv==0 else "KHONG_DAT","Khoa chinh bat buoc")

# -------------------------------------------------------
# 1.11 inventory - khoa ghep (snapshot_date, product_id)
# -------------------------------------------------------
tong = len(inventory)
null_inv_date = inventory["snapshot_date"].isna().sum()
null_inv_pid  = inventory["product_id"].isna().sum()
dup_inv = inventory.duplicated(subset=["snapshot_date","product_id"]).sum()
status_inv = "DAT" if (null_inv_date==0 and null_inv_pid==0 and dup_inv==0) else "KHONG_DAT"
print(f"[1.11] inventory (snapshot_date,product_id)  NULL_date={null_inv_date}  NULL_pid={null_inv_pid}  DUP={dup_inv}  => {status_inv}")
log("1.11","inventory","PK_NULL","snapshot_date",null_inv_date,tong,
    "DAT" if null_inv_date==0 else "KHONG_DAT","Phan cua khoa ghep")
log("1.11","inventory","PK_NULL","product_id",null_inv_pid,tong,
    "DAT" if null_inv_pid==0 else "KHONG_DAT","Phan cua khoa ghep")
log("1.11","inventory","PK_DUP","(snapshot_date,product_id)",dup_inv,tong,
    "DAT" if dup_inv==0 else "KHONG_DAT","Khoa ghep chinh")

# ============================================================
# PHAN 2: KHOA NGOAI (Foreign Key)
# ============================================================
print(f"\n{SEP}")
print("PHAN 2: KIEM TRA KHOA NGOAI")
print(SEP)

valid_customer_ids  = set(customers["customer_id"].dropna())
valid_zip           = set(geography["zip"].dropna())
valid_product_ids   = set(products["product_id"].dropna())
valid_promo_ids     = set(promotions["promo_id"].dropna())
valid_order_ids     = set(orders["order_id"].dropna())
valid_order_item_keys = set(zip(order_items["order_id"], order_items["product_id"]))

def kiem_tra_fk(bang_ten, df_con, cot_con, valid_set, bang_cha, cot_cha,
                cho_phep_null=True):
    tong = len(df_con)
    null_cnt = df_con[cot_con].isna().sum()
    # Chi kiem tra cac dong co gia tri (non-null)
    co_gia_tri = df_con[df_con[cot_con].notna()]
    orphan_mask = ~co_gia_tri[cot_con].isin(valid_set)
    orphan_cnt  = orphan_mask.sum()
    tong_kt     = len(co_gia_tri)

    if null_cnt > 0 and not cho_phep_null:
        null_status = "KHONG_DAT"
    else:
        null_status = "DAT"

    fk_status = "DAT" if orphan_cnt == 0 else "KHONG_DAT"

    print(f"  FK {bang_ten}.{cot_con} -> {bang_cha}.{cot_cha}: "
          f"NULL={null_cnt}  Orphan={orphan_cnt}/{tong_kt}  => NULL:{null_status} / FK:{fk_status}")

    log(f"FK",bang_ten,f"FK_NULL",cot_con,null_cnt,tong,
        null_status, f"FK -> {bang_cha}.{cot_cha}" + (" (bat buoc)" if not cho_phep_null else " (tuy chon)"))
    log(f"FK",bang_ten,f"FK_ORPHAN",cot_con,orphan_cnt,tong_kt,
        fk_status, f"FK -> {bang_cha}.{cot_cha}")

    if orphan_cnt > 0:
        orphan_rows = co_gia_tri[orphan_mask][[cot_con]].drop_duplicates().copy()
        log_issues(bang_ten, f"FK_ORPHAN_{cot_con}", cot_con, orphan_rows)

    return null_cnt, orphan_cnt

print("\n[orders FK]")
kiem_tra_fk("orders", orders, "customer_id", valid_customer_ids, "customers", "customer_id", cho_phep_null=False)
kiem_tra_fk("orders", orders, "zip", valid_zip, "geography", "zip", cho_phep_null=False)

print("\n[order_items FK]")
kiem_tra_fk("order_items", order_items, "order_id",    valid_order_ids,   "orders",     "order_id",   cho_phep_null=False)
kiem_tra_fk("order_items", order_items, "product_id",  valid_product_ids, "products",   "product_id", cho_phep_null=False)
kiem_tra_fk("order_items", order_items, "promo_id",    valid_promo_ids,   "promotions", "promo_id",   cho_phep_null=True)
kiem_tra_fk("order_items", order_items, "promo_id_2",  valid_promo_ids,   "promotions", "promo_id",   cho_phep_null=True)

print("\n[payments FK]")
null_pay_fk, orp_pay = kiem_tra_fk("payments", payments, "order_id", valid_order_ids, "orders", "order_id", cho_phep_null=False)
# Kiem tra them: orders khong co trong payments (1-1 ky vong)
orders_missing_payment = valid_order_ids - set(payments["order_id"].dropna())
print(f"  orders khong co trong payments: {len(orders_missing_payment)}")
log("FK","payments","FK_MISSING_PARENT","order_id",len(orders_missing_payment),len(orders),
    "DAT" if len(orders_missing_payment)==0 else "KHONG_DAT","Moi don phai co payment (1-1)")

print("\n[shipments FK]")
kiem_tra_fk("shipments", shipments, "order_id", valid_order_ids, "orders", "order_id", cho_phep_null=False)
# orders khong co trong shipments (co the hop le: don huy)
orders_missing_ship = valid_order_ids - set(shipments["order_id"].dropna())
pct_missing_ship = len(orders_missing_ship) / len(orders) * 100
print(f"  orders khong co trong shipments: {len(orders_missing_ship)} ({pct_missing_ship:.2f}%)")
log("FK","shipments","FK_MISSING_PARENT","order_id",len(orders_missing_ship),len(orders),
    "NEEDS_REVIEW" if len(orders_missing_ship)>0 else "DAT",
    "Don chua van chuyen co the la don huy/cho xu ly")

print("\n[returns FK]")
kiem_tra_fk("returns", returns, "order_id",   valid_order_ids,   "orders",   "order_id",   cho_phep_null=False)
kiem_tra_fk("returns", returns, "product_id", valid_product_ids, "products", "product_id", cho_phep_null=False)
# Kiem tra (order_id, product_id) trong returns phai ton tai trong order_items
ret_key = set(zip(returns["order_id"], returns["product_id"]))
orphan_ret_key = ret_key - valid_order_item_keys
print(f"  returns (order_id,product_id) khong co trong order_items: {len(orphan_ret_key)}")
log("FK","returns","FK_COMPOSITE_ORPHAN","(order_id,product_id)",len(orphan_ret_key),len(returns),
    "DAT" if len(orphan_ret_key)==0 else "KHONG_DAT",
    "Phai ton tai dong san pham trong order_items moi tra hang duoc")

print("\n[reviews FK]")
kiem_tra_fk("reviews", reviews, "order_id",    valid_order_ids,    "orders",    "order_id",    cho_phep_null=False)
kiem_tra_fk("reviews", reviews, "product_id",  valid_product_ids,  "products",  "product_id",  cho_phep_null=False)
kiem_tra_fk("reviews", reviews, "customer_id", valid_customer_ids, "customers", "customer_id", cho_phep_null=False)
# Kiem tra (order_id, product_id) trong reviews phai ton tai trong order_items
rev_key = set(zip(reviews["order_id"], reviews["product_id"]))
orphan_rev_key = rev_key - valid_order_item_keys
print(f"  reviews (order_id,product_id) khong co trong order_items: {len(orphan_rev_key)}")
log("FK","reviews","FK_COMPOSITE_ORPHAN","(order_id,product_id)",len(orphan_rev_key),len(reviews),
    "DAT" if len(orphan_rev_key)==0 else "KHONG_DAT",
    "Phai mua san pham moi duoc review")

print("\n[inventory FK]")
kiem_tra_fk("inventory", inventory, "product_id", valid_product_ids, "products", "product_id", cho_phep_null=False)

print("\n[customers FK]")
kiem_tra_fk("customers", customers, "zip", valid_zip, "geography", "zip", cho_phep_null=False)

# ============================================================
# PHAN 3: KIEU DU LIEU GIUA CAC KHOA LIEN KET
# ============================================================
print(f"\n{SEP}")
print("PHAN 3: KIEM TRA KIEU DU LIEU KHOA LIEN KET")
print(SEP)

dtype_checks = [
    ("orders.customer_id",     orders["customer_id"].dtype,     "customers.customer_id", customers["customer_id"].dtype),
    ("orders.zip",             orders["zip"].dtype,              "geography.zip",         geography["zip"].dtype),
    ("order_items.order_id",   order_items["order_id"].dtype,   "orders.order_id",       orders["order_id"].dtype),
    ("order_items.product_id", order_items["product_id"].dtype, "products.product_id",   products["product_id"].dtype),
    ("order_items.promo_id",   order_items["promo_id"].dtype,   "promotions.promo_id",   promotions["promo_id"].dtype),
    ("payments.order_id",      payments["order_id"].dtype,      "orders.order_id",       orders["order_id"].dtype),
    ("shipments.order_id",     shipments["order_id"].dtype,     "orders.order_id",       orders["order_id"].dtype),
    ("returns.order_id",       returns["order_id"].dtype,       "orders.order_id",       orders["order_id"].dtype),
    ("returns.product_id",     returns["product_id"].dtype,     "products.product_id",   products["product_id"].dtype),
    ("reviews.order_id",       reviews["order_id"].dtype,       "orders.order_id",       orders["order_id"].dtype),
    ("reviews.product_id",     reviews["product_id"].dtype,     "products.product_id",   products["product_id"].dtype),
    ("reviews.customer_id",    reviews["customer_id"].dtype,    "customers.customer_id", customers["customer_id"].dtype),
    ("inventory.product_id",   inventory["product_id"].dtype,   "products.product_id",   products["product_id"].dtype),
    ("customers.zip",          customers["zip"].dtype,          "geography.zip",         geography["zip"].dtype),
]

dt_issues = []
for con, dt_con, cha, dt_cha in dtype_checks:
    khop = (str(dt_con) == str(dt_cha))
    status_dt = "DAT" if khop else "NEEDS_REVIEW"
    print(f"  {con} ({dt_con}) -> {cha} ({dt_cha})  => {status_dt}")
    log("3",con.split(".")[0],"DTYPE_MISMATCH",con.split(".")[1],
        0 if khop else 1, 1, status_dt,
        f"{dt_con} vs {dt_cha}")
    if not khop:
        dt_issues.append({"Cot_con": con, "Dtype_con": str(dt_con),
                          "Cot_cha": cha, "Dtype_cha": str(dt_cha)})

# ============================================================
# PHAN 4: FILES NGOAI PHAM VI QUAN HE
# ============================================================
print(f"\n{SEP}")
print("PHAN 4: FILES NGOAI PHAM VI KIEM TRA QUAN HE")
print(SEP)
ngoai_pham_vi = ["sales.csv", "web_traffic.csv", "sample_submission.csv", "submission_idea42_alphaequal.csv"]
for f in ngoai_pham_vi:
    print(f"  {f}: Khong ap dung kiem tra FK - file tong hop / du bao (NEEDS_REVIEW tuong lai)")
    log("4", f.replace(".csv",""), "SCOPE_EXCLUDED", "N/A", 0, 0, "NEEDS_REVIEW",
        "File tong hop / du bao, chua xac dinh quan he voi bang nghiep vu")

# ============================================================
# XUAT KET QUA
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
print(df_report[["Ma_KT","Bang","Loai_kiem_tra","Cot","So_van_de","Tong_ban_ghi","Ty_le_%","Trang_thai"]].to_string(index=False))
print()
print("SO LUONG KIEM TRA THEO TRANG THAI:")
print(dem.to_string())
print("\n[GHI CHU] Day chi la buoc KIEM TRA. Chua thuc hien lam sach hoac sua du lieu.")
