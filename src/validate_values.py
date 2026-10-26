"""
KT8 - Kiem tra kieu du lieu va gia tri bat thuong (Data Quality & Value Validation)
Kem khao sat du lieu tong quan va kiem tra nhat quan khuyen mai KT1-KT6c tu clean_data.py
Fashion_DW_Project

Pham vi: 13 file CSV nghiep vu trong data/raw/
Ngoai pham vi: sample_submission.csv, submission_idea42_alphaequal.csv

Nguyen tac:
  - Chi kiem tra va phan loai. Khong sua, khong xoa, khong them du lieu.
  - Du lieu trong data/raw/ duoc giu nguyen 100%.
  - Phan biet LOI (vi pham chac chan) voi NGHI_VAN (can xem xet nghiep vu).

Ket qua xuat ra:
  docs/value_validation_report.csv       -- tong hop 63 tieu chi KT8
  docs/value_validation_issues.csv       -- danh sach ban ghi KT8 co van de
  docs/promotion_category_summary.csv    -- tom tat 10 chuong trinh promo KT6c

Chay doc lap:
  python src/validate_values.py
"""

import pandas as pd
import numpy as np
from pathlib import Path

# ─── Duong dan ────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR  = BASE_DIR / "data" / "raw"
DOCS_DIR = BASE_DIR / "docs"
DOCS_DIR.mkdir(parents=True, exist_ok=True)

SEP = "=" * 65

# ─── Bo tich luy ket qua KT8 ──────────────────────────────────────────────────
report_rows = []   # Tong hop 63 tieu chi KT8
issue_rows  = []   # Danh sach ban ghi co van de cu the

def log(ma, bang, kiem_tra, mo_ta, so_van_de, tong, trang_thai, ghi_chu):
    """Ghi mot dong vao bang tong hop KT8."""
    report_rows.append({
        "Ma_KT":        ma,
        "Bang":         bang,
        "Ten_KT":       kiem_tra,
        "Mo_ta":        mo_ta,
        "So_van_de":    so_van_de,
        "Tong_KT":      tong,
        "Ty_le_%":      round(so_van_de / tong * 100, 4) if tong > 0 else 0,
        "Trang_thai":   trang_thai,
        "Ghi_chu":      ghi_chu,
    })

def save_issues(df_sub, bang, ma_kt, mo_ta_van_de):
    """Ghi cac ban ghi cu the vao danh sach van de."""
    if df_sub is not None and len(df_sub) > 0:
        tmp = df_sub.copy()
        tmp.insert(0, "_bang",   bang)
        tmp.insert(1, "_ma_kt",  ma_kt)
        tmp.insert(2, "_van_de", mo_ta_van_de)
        issue_rows.append(tmp)

def st(so_van_de, muc="LOI"):
    """Xac dinh trang thai: DAT neu khong co van de, nguoc lai theo muc LOI / NGHI_VAN."""
    return muc if so_van_de > 0 else "DAT"

# ─── Cac ham kiem tra dung chung cho KT8 ───────────────────────────────────────
def check_range(ma, bang, condition, mo_ta, ghi_chu, muc="LOI", df=None):
    """Kiem tra khoang gia tri hoac dieu kien am/duong."""
    n = len(df) if df is not None else len(dfs[bang])
    bad_cnt = int(condition.sum())
    print(f"[{ma}] {mo_ta}: {bad_cnt}")
    log(ma, bang, "VALUE_RANGE", mo_ta, bad_cnt, n, st(bad_cnt, muc), ghi_chu)
    return bad_cnt

def check_enum(ma, bang, col_name, valid_set, mo_ta, ghi_chu=None, muc="LOI"):
    """Kiem tra tap gia tri hop le (danh muc / enum)."""
    df = dfs[bang]
    n = len(df)
    bad_cnt = int((~df[col_name].isin(valid_set)).sum())
    print(f"[{ma}] {col_name} ngoai tap hop: {bad_cnt}")
    log(ma, bang, "VALUE_ENUM", mo_ta, bad_cnt, n, st(bad_cnt, muc),
        ghi_chu if ghi_chu else f"Gia tri hop le: {valid_set}")
    return bad_cnt

def check_between(ma, bang, col_name, lower, upper, mo_ta, ghi_chu, muc="LOI"):
    """Kiem tra gia tri nam trong doan [lower, upper]."""
    df = dfs[bang]
    n = len(df)
    bad_cnt = int((~df[col_name].between(lower, upper)).sum())
    print(f"[{ma}] {col_name} ngoai [{lower},{upper}]: {bad_cnt}")
    log(ma, bang, "VALUE_RANGE", mo_ta, bad_cnt, n, st(bad_cnt, muc), ghi_chu)
    return bad_cnt

def check_date_parse(ma, bang, col_name, ghi_chu=""):
    """Kiem tra loi dinh dang parse ngay thang."""
    df = dfs[bang]
    n = len(df)
    bad_cnt = int(df[col_name].isna().sum())
    print(f"[{ma}] {col_name} parse fail: {bad_cnt}")
    log(ma, bang, "DTYPE_DATE", f"{col_name} parse errors", bad_cnt, n, st(bad_cnt), ghi_chu)
    return bad_cnt

def check_future_date(ma, bang, col_name, mo_ta, ghi_chu):
    """Kiem tra ngay thang nam trong tuong lai."""
    df = dfs[bang]
    n = len(df)
    bad_cnt = int((df[col_name] > pd.Timestamp.now()).sum())
    print(f"[{ma}] {col_name} in future: {bad_cnt}")
    log(ma, bang, "VALUE_FUTURE", mo_ta, bad_cnt, n, st(bad_cnt), ghi_chu)
    return bad_cnt

def check_duplicate(ma, bang, col_name, mo_ta, ghi_chu, muc="LOI"):
    """Kiem tra trung lap tren mot cot."""
    df = dfs[bang]
    n = len(df)
    bad_cnt = int(df[col_name].duplicated().sum())
    print(f"[{ma}] {col_name} trung lap: {bad_cnt}")
    log(ma, bang, "DUPLICATE", mo_ta, bad_cnt, n, st(bad_cnt, muc), ghi_chu)
    return bad_cnt

# ─── Nap 13 bang nghiep vu ────────────────────────────────────────────────────
print("Dang nap du lieu...")
dfs = {
    "customers":   pd.read_csv(RAW_DIR / "customers.csv",   low_memory=False, parse_dates=["signup_date"]),
    "geography":   pd.read_csv(RAW_DIR / "geography.csv",   low_memory=False),
    "inventory":   pd.read_csv(RAW_DIR / "inventory.csv",   low_memory=False, parse_dates=["snapshot_date"]),
    "order_items": pd.read_csv(RAW_DIR / "order_items.csv", low_memory=False),
    "orders":      pd.read_csv(RAW_DIR / "orders.csv",      low_memory=False, parse_dates=["order_date"]),
    "payments":    pd.read_csv(RAW_DIR / "payments.csv",    low_memory=False),
    "products":    pd.read_csv(RAW_DIR / "products.csv",    low_memory=False),
    "promotions":  pd.read_csv(RAW_DIR / "promotions.csv",  low_memory=False, parse_dates=["start_date", "end_date"]),
    "returns":     pd.read_csv(RAW_DIR / "returns.csv",     low_memory=False, parse_dates=["return_date"]),
    "reviews":     pd.read_csv(RAW_DIR / "reviews.csv",     low_memory=False, parse_dates=["review_date"]),
    "sales":       pd.read_csv(RAW_DIR / "sales.csv",       low_memory=False, parse_dates=["Date"]),
    "shipments":   pd.read_csv(RAW_DIR / "shipments.csv",   low_memory=False, parse_dates=["ship_date", "delivery_date"]),
    "web_traffic": pd.read_csv(RAW_DIR / "web_traffic.csv", low_memory=False, parse_dates=["date"]),
}

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
sales       = dfs["sales"]
shipments   = dfs["shipments"]
web         = dfs["web_traffic"]

print("Nap xong. Bat dau kiem tra...\n")

# =============================================================================
# PHAN A — KHAO SAT DU LIEU TONG QUAN (chuyen tu clean_data.py)
# =============================================================================
print(SEP)
print("PHAN A: KHAO SAT DU LIEU NGUON")
print(SEP)
for name, df in dfs.items():
    null_cnt = int(df.isnull().sum().sum())
    dup_cnt  = int(df.duplicated().sum())
    print(f"  {name:<14}: {df.shape[0]:>7,} dong, {df.shape[1]:>2} cot, NULL={null_cnt:>8,}, DUP={dup_cnt:>4}")

# =============================================================================
# PHAN B — KT8: KIEM TRA GIA TRI VA NGHIEP VU 13 BANG (63 tieu chi)
# =============================================================================
print(f"\n{SEP}")
print("PHAN B: KT8 - KIEM TRA GIA TRI VA NGHIEP VU")
print(SEP)

# ─── 1. CUSTOMERS ─────────────────────────────────────────────────────────────
print(f"\n{SEP}"); print("PHAN 1: customers.csv"); print(SEP)
check_date_parse("1.1", "customers", "signup_date", "Kiem tra dinh dang ngay")
check_future_date("1.2", "customers", "signup_date", "signup_date > today", "Khach hang chua the dang ky trong tuong lai")
check_enum("1.3", "customers", "gender", {"Male", "Female", "Non-binary"}, "gender invalid", "Gia tri hop le: {'Female', 'Male', 'Non-binary'}")
check_enum("1.4", "customers", "age_group", {"18-24", "25-34", "35-44", "45-54", "55+"}, "age_group invalid", "Gia tri hop le: {'45-54', '35-44', '25-34', '18-24', '55+'}")
check_enum("1.5", "customers", "acquisition_channel",
           {"direct", "email_campaign", "organic_search", "paid_search", "referral", "social_media"},
           "acquisition_channel invalid",
           "Gia tri hop le: {'direct', 'referral', 'social_media', 'paid_search', 'organic_search', 'email_campaign'}")

# ─── 2. GEOGRAPHY ─────────────────────────────────────────────────────────────
print(f"\n{SEP}"); print("PHAN 2: geography.csv"); print(SEP)
check_range("2.1", "geography", geography["zip"] <= 0, "zip <= 0", "Ma buu chinh phai la so duong")
valid_region = set(geography["region"].dropna().unique())
print(f"[2.2] geography.region distinct: {sorted(valid_region)}")
log("2.2", "geography", "VALUE_ENUM", "region distinct values", 0, len(geography), "DAT", f"Distinct: {sorted(valid_region)}")

# ─── 3. PRODUCTS ──────────────────────────────────────────────────────────────
print(f"\n{SEP}"); print("PHAN 3: products.csv"); print(SEP)
n_p = len(products)
check_range("3.1", "products", products["price"] <= 0, "price <= 0", "Gia ban phai duong")
check_range("3.2", "products", products["cogs"] <= 0, "cogs <= 0", "Gia von phai duong")

cogs_over = products["cogs"] > products["price"]
print(f"[3.3] cogs > price: {cogs_over.sum()}")
log("3.3", "products", "LOGIC", "cogs > price", int(cogs_over.sum()), n_p, st(int(cogs_over.sum())), "Ban duoi gia von la bat thuong nghiep vu")
save_issues(products[cogs_over], "products", "3.3", "cogs > price")

margin = (products["price"] - products["cogs"]) / products["price"] * 100
low_margin = (margin < 5).sum()
print(f"[3.4] gross margin < 5%%: {low_margin}")
log("3.4", "products", "VALUE_RANGE", "gross_margin < 5%", int(low_margin), n_p, st(int(low_margin), "NGHI_VAN"), "Bien lai thap bat thuong, can xem xet nghiep vu")

check_enum("3.5", "products", "category", {"Casual", "GenZ", "Outdoor", "Streetwear"}, "category invalid", "Gia tri hop le: {'Streetwear', 'GenZ', 'Casual', 'Outdoor'}")

# ─── 4. PROMOTIONS ────────────────────────────────────────────────────────────
print(f"\n{SEP}"); print("PHAN 4: promotions.csv"); print(SEP)
n_pr = len(promotions)
check_range("4.1", "promotions", promotions["discount_value"] < 0, "discount_value < 0", "Muc giam gia khong the am")

pct_mask = promotions["promo_type"] == "percentage"
pct_over = (pct_mask & (promotions["discount_value"] > 100)).sum()
print(f"[4.2] percentage discount_value > 100: {pct_over}")
log("4.2", "promotions", "VALUE_RANGE", "pct discount_value > 100%", int(pct_over), int(pct_mask.sum()), st(int(pct_over)), "Giam gia phan tram khong the vuot 100%")

invalid_dates = (promotions["end_date"] < promotions["start_date"]).sum()
print(f"[4.3] end_date < start_date: {invalid_dates}")
log("4.3", "promotions", "TIME_ORDER", "end_date < start_date", int(invalid_dates), n_pr, st(int(invalid_dates)), "Ngay ket thuc phai sau ngay bat dau")
bad_promo_dates = promotions[promotions["end_date"] < promotions["start_date"]]
save_issues(bad_promo_dates, "promotions", "4.3", "end_date < start_date")

check_enum("4.4", "promotions", "stackable_flag", {0, 1}, "stackable_flag not in {0,1}", "Flag phai la 0 hoac 1")
check_range("4.5", "promotions", promotions["min_order_value"] < 0, "min_order_value < 0", "Nguong don hang toi thieu khong the am")

# ─── 5. ORDERS ────────────────────────────────────────────────────────────────
print(f"\n{SEP}"); print("PHAN 5: orders.csv"); print(SEP)
n_o = len(orders)
check_date_parse("5.1", "orders", "order_date", "Kiem tra dinh dang ngay")
check_future_date("5.2", "orders", "order_date", "order_date > today", "Don hang khong the o tuong lai")
check_enum("5.3", "orders", "order_status", {"created", "paid", "shipped", "delivered", "returned", "cancelled"}, "order_status invalid", "Gia tri hop le: {'shipped', 'returned', 'created', 'cancelled', 'paid', 'delivered'}")
check_enum("5.4", "orders", "payment_method", {"credit_card", "cod", "paypal", "bank_transfer", "apple_pay"}, "payment_method invalid", "Gia tri hop le: {'apple_pay', 'cod', 'paypal', 'bank_transfer', 'credit_card'}")
check_enum("5.5", "orders", "device_type", {"desktop", "mobile", "tablet"}, "device_type invalid", "Gia tri hop le: {'desktop', 'mobile', 'tablet'}")

# 5.6 order_date < customer signup_date
merged_co = orders[["order_id", "customer_id", "order_date"]].merge(
    customers[["customer_id", "signup_date"]], on="customer_id", how="left"
)
before_signup = merged_co["order_date"] < merged_co["signup_date"]
n_before = int(before_signup.sum())
print(f"[5.6] order_date < customer signup_date: {n_before} ({n_before/n_o*100:.2f}%) — xem ghi chu")
log("5.6", "orders", "TIME_ORDER", "order_date < customer signup_date",
    n_before, n_o, "NGHI_VAN" if n_before > 0 else "DAT",
    "signup_date co the la ngay cap nhat ho so, khong phai ngay dang ky lan dau. "
    "Ti le 73.7% cho thay day la dac trung du lieu, can xac minh voi chu du an.")
save_issues(merged_co[before_signup].head(500), "orders", "5.6", "order_date < signup_date (500-row sample)")

# ─── 6. ORDER ITEMS ───────────────────────────────────────────────────────────
print(f"\n{SEP}"); print("PHAN 6: order_items.csv"); print(SEP)
n_oi = len(order_items)
check_range("6.1", "order_items", order_items["quantity"] <= 0, "quantity <= 0", "So luong phai la so nguyen duong")
check_range("6.2", "order_items", order_items["unit_price"] <= 0, "unit_price <= 0", "Don gia phai duong")
check_range("6.3", "order_items", order_items["discount_amount"] < 0, "discount_amount < 0", "Giam gia khong the am")

total_line_val = order_items["unit_price"] * order_items["quantity"]
discount_over = order_items["discount_amount"] > total_line_val
n_dov = int(discount_over.sum())
print(f"[6.4] discount_amount > unit_price*quantity: {n_dov}")
log("6.4", "order_items", "LOGIC", "discount_amount > total_line_value",
    n_dov, n_oi, st(n_dov), "Giam gia khong the lon hon gia tri dong hang")
save_issues(order_items[discount_over], "order_items", "6.4", "discount_amount > total line value")

promo_no_discount = int((order_items["promo_id"].notna() & (order_items["discount_amount"] == 0)).sum())
print(f"[6.5] promo_id co gia tri nhung discount_amount=0: {promo_no_discount}")
log("6.5", "order_items", "LOGIC", "promo_id set but discount=0",
    promo_no_discount, n_oi, st(promo_no_discount, "NGHI_VAN"),
    "Co the la KM ngoai thi truong (free shipping) nhung can xac nhan")

no_promo_has_discount = int((order_items["promo_id"].isna() & order_items["promo_id_2"].isna() & (order_items["discount_amount"] > 0)).sum())
print(f"[6.6] khong co promo nhung discount_amount > 0: {no_promo_has_discount}")
log("6.6", "order_items", "LOGIC", "no promo_id but discount_amount > 0",
    no_promo_has_discount, n_oi, st(no_promo_has_discount, "NGHI_VAN"),
    "Can xac nhan: co the la giam gia tho cong hoac thieu promo_id")

# ─── 7. PAYMENTS ──────────────────────────────────────────────────────────────
print(f"\n{SEP}"); print("PHAN 7: payments.csv"); print(SEP)
n_pay = len(payments)
check_range("7.1", "payments", payments["payment_value"] <= 0, "payment_value <= 0", "Gia tri thanh toan phai duong")
bad_inst = check_enum("7.2", "payments", "installments", {1, 2, 3, 6, 12}, "installments invalid",
                      f"Gia tri quan sat: {sorted(payments['installments'].unique())} — xac nhan chinh sach tra gop",
                      muc="NGHI_VAN")

oi_total = (
    order_items
    .assign(_total=order_items["unit_price"] * order_items["quantity"] - order_items["discount_amount"])
    .groupby("order_id")["_total"].sum()
    .reset_index(name="computed_total")
)
merged_pay = payments.merge(oi_total, on="order_id", how="inner")
diff = (merged_pay["payment_value"] - merged_pay["computed_total"]).abs()
n_diff = int((diff > 0.01).sum())
print(f"[7.3] payment_value khac computed total > 0.01: {n_diff}  max_diff={diff.max():.4f}")
log("7.3", "payments", "LOGIC", "payment_value != sum(line_totals)",
    n_diff, len(merged_pay), st(n_diff), "Gia tri thanh toan phai khop voi tong dong hang sau giam gia")

# ─── 8. SHIPMENTS ─────────────────────────────────────────────────────────────
print(f"\n{SEP}"); print("PHAN 8: shipments.csv"); print(SEP)
n_sh = len(shipments)
check_date_parse("8.1", "shipments", "ship_date", "")
check_date_parse("8.2", "shipments", "delivery_date", "")

del_before_ship = int((shipments["delivery_date"] < shipments["ship_date"]).sum())
print(f"[8.3] delivery_date < ship_date: {del_before_ship}")
log("8.3", "shipments", "TIME_ORDER", "delivery_date < ship_date",
    del_before_ship, n_sh, st(del_before_ship), "Khong the giao hang truoc khi xuat kho")
save_issues(shipments[shipments["delivery_date"] < shipments["ship_date"]],
            "shipments", "8.3", "delivery_date < ship_date")

merged_ship = shipments.merge(orders[["order_id", "order_date"]], on="order_id", how="inner")
ship_before_order = int((merged_ship["ship_date"] < merged_ship["order_date"]).sum())
print(f"[8.4] ship_date < order_date: {ship_before_order}")
log("8.4", "shipments", "TIME_ORDER", "ship_date < order_date",
    ship_before_order, len(merged_ship), st(ship_before_order), "Khong the xuat kho truoc khi dat hang")
save_issues(merged_ship[merged_ship["ship_date"] < merged_ship["order_date"]],
            "shipments", "8.4", "ship_date < order_date")

check_range("8.5", "shipments", shipments["shipping_fee"] < 0, "shipping_fee < 0", "Phi van chuyen khong the am")
zero_fee = int((shipments["shipping_fee"] == 0).sum())
print(f"[8.6] shipping_fee = 0: {zero_fee} ({zero_fee/n_sh*100:.2f}%)")
log("8.6", "shipments", "VALUE_ZERO", "shipping_fee = 0",
    zero_fee, n_sh, "NGHI_VAN" if zero_fee > 0 else "DAT", "Co the la chinh sach mien phi van chuyen, can xac nhan")

# ─── 9. RETURNS ───────────────────────────────────────────────────────────────
print(f"\n{SEP}"); print("PHAN 9: returns.csv"); print(SEP)
n_ret = len(returns)
check_date_parse("9.1", "returns", "return_date", "")

merged_ret = returns.merge(orders[["order_id", "order_date"]], on="order_id", how="left")
ret_before_order = int((merged_ret["return_date"] < merged_ret["order_date"]).sum())
print(f"[9.2] return_date < order_date: {ret_before_order}")
log("9.2", "returns", "TIME_ORDER", "return_date < order_date",
    ret_before_order, n_ret, st(ret_before_order), "Khong the tra hang truoc khi dat hang")
save_issues(merged_ret[merged_ret["return_date"] < merged_ret["order_date"]],
            "returns", "9.2", "return_date < order_date")

check_range("9.3", "returns", returns["return_quantity"] <= 0, "return_quantity <= 0", "So luong tra hang phai duong")

# 9.4 return_quantity > bought_quantity (tong hop theo order_id, product_id)
# Quan trong: Tong hop quantity theo (order_id, product_id) tranh false positive cho RET-043492
oi_qty = (
    order_items.groupby(["order_id", "product_id"], as_index=False)["quantity"]
    .sum()
    .rename(columns={"quantity": "bought_qty"})
)
ret_agg = (
    returns.groupby(["order_id", "product_id"], as_index=False)["return_quantity"]
    .sum()
    .rename(columns={"return_quantity": "total_returned_qty"})
)
merged_rq = ret_agg.merge(oi_qty, on=["order_id", "product_id"], how="left")
over_return = merged_rq["total_returned_qty"] > merged_rq["bought_qty"]
n_over = int(over_return.sum())
print(f"[9.4] return_quantity > bought_quantity: {n_over}")
log("9.4", "returns", "LOGIC", "return_quantity > bought_quantity",
    n_over, n_ret, st(n_over), "Tong so luong tra khong the vuot tong so luong da mua")
if n_over > 0:
    save_issues(merged_rq[over_return][["order_id", "product_id", "total_returned_qty", "bought_qty"]],
                "returns", "9.4", "return_quantity > bought_quantity")

check_range("9.5", "returns", returns["refund_amount"] <= 0, "refund_amount <= 0", "So tien hoan tra phai duong")
check_enum("9.6", "returns", "return_reason",
           {"changed_mind", "defective", "late_delivery", "not_as_described", "wrong_size"},
           "return_reason invalid",
           "Gia tri hop le: {'defective', 'late_delivery', 'changed_mind', 'not_as_described', 'wrong_size'}")

# ─── 10. REVIEWS ──────────────────────────────────────────────────────────────
print(f"\n{SEP}"); print("PHAN 10: reviews.csv"); print(SEP)
n_rev = len(reviews)
check_between("10.1", "reviews", "rating", 1, 5, "rating not in [1,5]", "Rating phai tu 1 den 5")

merged_rv = reviews.merge(orders[["order_id", "order_date"]], on="order_id", how="left")
rv_before_order = int((merged_rv["review_date"] < merged_rv["order_date"]).sum())
print(f"[10.2] review_date < order_date: {rv_before_order}")
log("10.2", "reviews", "TIME_ORDER", "review_date < order_date",
    rv_before_order, n_rev, st(rv_before_order), "Khong the danh gia truoc khi dat hang")
save_issues(merged_rv[merged_rv["review_date"] < merged_rv["order_date"]],
            "reviews", "10.2", "review_date < order_date")

merged_rv_d = reviews.merge(shipments[["order_id", "delivery_date"]], on="order_id", how="left")
rv_before_del = int((merged_rv_d["review_date"] < merged_rv_d["delivery_date"]).sum())
print(f"[10.3] review_date < delivery_date: {rv_before_del} (nghi van)")
log("10.3", "reviews", "TIME_ORDER", "review_date < delivery_date",
    rv_before_del, int(merged_rv_d["delivery_date"].notna().sum()),
    "NGHI_VAN" if rv_before_del > 0 else "DAT",
    "Mot so he thong cho phep danh gia ngay sau khi dat hang; can xac nhan chinh sach cua san")

# ─── 11. INVENTORY ────────────────────────────────────────────────────────────
print(f"\n{SEP}"); print("PHAN 11: inventory.csv"); print(SEP)
check_range("11.1", "inventory", inventory["stock_on_hand"] < 0, "stock_on_hand < 0", "Ton kho khong the am")
check_between("11.2", "inventory", "fill_rate", 0, 1, "fill_rate not in [0,1]", "Fill rate la ty le, phai trong [0,1]")
check_between("11.3", "inventory", "sell_through_rate", 0, 1, "sell_through_rate not in [0,1]", "Sell-through rate la ty le, phai trong [0,1]")

all_zero_reorder = bool((inventory["reorder_flag"] == 0).all())
print(f"[11.4] reorder_flag luon = 0: {all_zero_reorder} => NGHI_VAN")
log("11.4", "inventory", "VALUE_CONST", "reorder_flag always 0",
    1 if all_zero_reorder else 0, 1, "NGHI_VAN" if all_zero_reorder else "DAT",
    "reorder_flag luon bang 0 tren toan bo 60,247 ban ghi — co the do logic tai tao du lieu hoac chinh sach kho chua duoc kich hoat")

check_enum("11.5", "inventory", "stockout_flag", {0, 1}, "stockout_flag not in {0,1}", "Flag phai la 0 hoac 1")
check_enum("11.6", "inventory", "overstock_flag", {0, 1}, "overstock_flag not in {0,1}", "Flag phai la 0 hoac 1")
check_range("11.7", "inventory", inventory["units_sold"] < 0, "units_sold < 0", "So luong ban khong the am")

# ─── 12. SALES ────────────────────────────────────────────────────────────────
print(f"\n{SEP}"); print("PHAN 12: sales.csv"); print(SEP)
n_sales = len(sales)
check_range("12.1", "sales", sales["Revenue"] <= 0, "Revenue <= 0", "Doanh thu phai duong")
check_range("12.2", "sales", sales["COGS"] <= 0, "COGS <= 0", "Chi phi von phai duong")

cogs_over_rev = int((sales["COGS"] > sales["Revenue"]).sum())
print(f"[12.3] COGS > Revenue: {cogs_over_rev}")
log("12.3", "sales", "LOGIC", "COGS > Revenue",
    cogs_over_rev, n_sales, st(cogs_over_rev, "NGHI_VAN"), "Ban lo tren tong hop ngay — can xac nhan voi don vi nghiep vu")
save_issues(sales[sales["COGS"] > sales["Revenue"]], "sales", "12.3", "COGS > Revenue (ban lo)")

check_duplicate("12.4", "sales", "Date", "Date duplicated", "Moi ngay chi co 1 ban ghi tong hop")

# ─── 13. WEB TRAFFIC ──────────────────────────────────────────────────────────
print(f"\n{SEP}"); print("PHAN 13: web_traffic.csv"); print(SEP)
n_web = len(web)
sess_lt_uv = int((web["sessions"] < web["unique_visitors"]).sum())
print(f"[13.1] sessions < unique_visitors: {sess_lt_uv}")
log("13.1", "web_traffic", "LOGIC", "sessions < unique_visitors",
    sess_lt_uv, n_web, st(sess_lt_uv, "NGHI_VAN"), "Mot nguoi co the tao nhieu phien; sessions thuong >= unique_visitors")

check_between("13.2", "web_traffic", "bounce_rate", 0, 1, "bounce_rate not in [0,1]", "Ty le bounce phai trong [0,1]")
check_range("13.3", "web_traffic", web["avg_session_duration_sec"] < 0, "avg_session_duration_sec < 0", "Thoi gian phien khong the am")
check_duplicate("13.4", "web_traffic", "date", "date duplicated", "Co the co nhieu dong/nguon traffic cung ngay — kiem tra traffic_source", muc="NGHI_VAN")

pv_lt_sess = int((web["page_views"] < web["sessions"]).sum())
print(f"[13.5] page_views < sessions: {pv_lt_sess}")
log("13.5", "web_traffic", "LOGIC", "page_views < sessions",
    pv_lt_sess, n_web, st(pv_lt_sess, "NGHI_VAN"), "Trung binh page_views/session phai >= 1")

# =============================================================================
# XUAT KET QUA KT8
# =============================================================================
print(f"\n{SEP}"); print("XUAT KET QUA KT8"); print(SEP)
df_report = pd.DataFrame(report_rows)
report_path = DOCS_DIR / "value_validation_report.csv"
df_report.to_csv(report_path, index=False, encoding="utf-8-sig")
print(f"[OK] Bao cao tong hop : {report_path} ({len(df_report)} muc)")

issues_path = DOCS_DIR / "value_validation_issues.csv"
if issue_rows:
    df_issues = pd.concat(issue_rows, ignore_index=True)
    df_issues.to_csv(issues_path, index=False, encoding="utf-8-sig")
    print(f"[OK] Danh sach van de : {issues_path} ({len(df_issues)} dong)")
else:
    pd.DataFrame().to_csv(issues_path, index=False, encoding="utf-8-sig")

# =============================================================================
# PHAN C — KIEM TRA KHUYEN MAI KT1-KT6c & KT6c CHI TIET (tu clean_data.py)
# =============================================================================
print(f"\n{SEP}")
print("PHAN C: KIEM TRA KHUYEN MAI (KT1 - KT6c & KT6c CHI TIET)")
print(SEP)

tong_dong_oi = len(order_items)
valid_promo_ids = set(promotions["promo_id"].dropna().unique())

# KT1: promo_id not null & discount_amount == 0
so_luong_1 = int((order_items["promo_id"].notna() & (order_items["discount_amount"] == 0)).sum())
# KT2: no promo & discount_amount > 0
so_luong_2 = int((order_items["promo_id"].isna() & order_items["promo_id_2"].isna() & (order_items["discount_amount"] > 0)).sum())
# KT3: has promo_id_2 but promo_id is null
so_luong_3 = int((order_items["promo_id_2"].notna() & order_items["promo_id"].isna()).sum())
# KT4a: promo_id not in promotions
so_luong_4a = int((order_items["promo_id"].notna() & ~order_items["promo_id"].isin(valid_promo_ids)).sum())
# KT4b: promo_id_2 not in promotions
so_luong_4b = int((order_items["promo_id_2"].notna() & ~order_items["promo_id_2"].isin(valid_promo_ids)).sum())
# KT5: discount_amount < 0
so_luong_5 = int((order_items["discount_amount"] < 0).sum())
# KT6a: promo_id null
null_promo1 = int(order_items["promo_id"].isna().sum())
# KT6b: promo_id_2 null
null_promo2 = int(order_items["promo_id_2"].isna().sum())
# KT6c: promotions.applicable_category null
null_cat = int(promotions["applicable_category"].isna().sum())
tong_promo = len(promotions)

promo_checks = [
    {"Ma_kiem_tra": "KT1",  "Mo_ta": "Co promo_id nhung discount_amount = 0",               "So_ban_ghi": so_luong_1,  "Ty_le_%": round(so_luong_1 / tong_dong_oi * 100, 4),  "Danh_gia": "Bat thuong - can kiem tra them" if so_luong_1 > 0 else "Binh thuong"},
    {"Ma_kiem_tra": "KT2",  "Mo_ta": "Khong co promo nhung discount_amount > 0",             "So_ban_ghi": so_luong_2,  "Ty_le_%": round(so_luong_2 / tong_dong_oi * 100, 4),  "Danh_gia": "Nghi van - can xac minh nguon goc giam gia" if so_luong_2 > 0 else "Binh thuong"},
    {"Ma_kiem_tra": "KT3",  "Mo_ta": "Co promo_id_2 nhung thieu promo_id",                   "So_ban_ghi": so_luong_3,  "Ty_le_%": round(so_luong_3 / tong_dong_oi * 100, 4),  "Danh_gia": "Bat thuong ve logic - can kiem tra" if so_luong_3 > 0 else "Binh thuong"},
    {"Ma_kiem_tra": "KT4a", "Mo_ta": "promo_id khong ton tai trong promotions",              "So_ban_ghi": so_luong_4a, "Ty_le_%": round(so_luong_4a / tong_dong_oi * 100, 4), "Danh_gia": "Loi tham chieu - can xac minh" if so_luong_4a > 0 else "Hop le"},
    {"Ma_kiem_tra": "KT4b", "Mo_ta": "promo_id_2 khong ton tai trong promotions",            "So_ban_ghi": so_luong_4b, "Ty_le_%": round(so_luong_4b / tong_dong_oi * 100, 4), "Danh_gia": "Loi tham chieu - can xac minh" if so_luong_4b > 0 else "Hop le"},
    {"Ma_kiem_tra": "KT5",  "Mo_ta": "discount_amount co gia tri am",                        "So_ban_ghi": so_luong_5,  "Ty_le_%": round(so_luong_5 / tong_dong_oi * 100, 4),  "Danh_gia": "Loi du lieu - can xu ly" if so_luong_5 > 0 else "Binh thuong"},
    {"Ma_kiem_tra": "KT6a", "Mo_ta": "NULL: order_items.promo_id",                           "So_ban_ghi": null_promo1, "Ty_le_%": round(null_promo1 / tong_dong_oi * 100, 4), "Danh_gia": "Binh thuong - don hang khong ap khuyen mai"},
    {"Ma_kiem_tra": "KT6b", "Mo_ta": "NULL: order_items.promo_id_2",                         "So_ban_ghi": null_promo2, "Ty_le_%": round(null_promo2 / tong_dong_oi * 100, 4), "Danh_gia": "Binh thuong - khong xep chong khuyen mai"},
    {"Ma_kiem_tra": "KT6c", "Mo_ta": "NULL: promotions.applicable_category",                "So_ban_ghi": null_cat,    "Ty_le_%": round(null_cat / tong_promo * 100, 4),       "Danh_gia": "Co the hop le - khuyen mai cho tat ca danh muc"},
]
df_promo_rep = pd.DataFrame(promo_checks)
print("\nTONG HOP KET QUA KIEM TRA KHUYEN MAI (KT1 - KT6c):")
print(df_promo_rep[["Ma_kiem_tra", "Mo_ta", "So_ban_ghi", "Ty_le_%", "Danh_gia"]].to_string(index=False))

# KT6c: Kiem tra chi tiet danh muc san pham vs applicable_category (30.061 luot)
promo_co_category = promotions[promotions["applicable_category"].notna()][["promo_id", "applicable_category"]].copy()
product_category_map = products[["product_id", "category"]].drop_duplicates()

def lay_giao_dich(cot_promo, nhan_promo):
    sub = order_items[order_items[cot_promo].isin(promo_co_category["promo_id"])][
        ["order_id", "product_id", "discount_amount", cot_promo]
    ].copy()
    sub = sub.rename(columns={cot_promo: "ma_promo_su_dung"})
    sub["loai_promo"] = nhan_promo
    return sub.merge(promo_co_category.rename(columns={"promo_id": "ma_promo_su_dung"}), on="ma_promo_su_dung", how="left")

gd_p1 = lay_giao_dich("promo_id", "promo_id_chinh")
gd_p2 = lay_giao_dich("promo_id_2", "promo_id_phu")
giao_dich = pd.concat([gd_p1, gd_p2], ignore_index=True)
giao_dich = giao_dich.merge(product_category_map.rename(columns={"category": "product_category"}), on="product_id", how="left")

# Phan loai vector hoa
giao_dich["ket_qua_kiem_tra"] = np.where(
    giao_dich["product_category"].isna(),
    "UNVERIFIABLE",
    np.where(giao_dich["product_category"] == giao_dich["applicable_category"], "HOP_LE", "REVIEW_REQUIRED")
)

# Tom tat theo ma khuyen mai
tom_tat_promo = (
    giao_dich.groupby(["ma_promo_su_dung", "applicable_category", "ket_qua_kiem_tra"])
    .size()
    .reset_index(name="so_giao_dich")
    .pivot_table(
        index=["ma_promo_su_dung", "applicable_category"],
        columns="ket_qua_kiem_tra",
        values="so_giao_dich",
        fill_value=0,
    )
    .reset_index()
)
for col in ["HOP_LE", "REVIEW_REQUIRED", "UNVERIFIABLE"]:
    if col not in tom_tat_promo.columns:
        tom_tat_promo[col] = 0

tom_tat_promo["TONG"] = tom_tat_promo["HOP_LE"] + tom_tat_promo["REVIEW_REQUIRED"] + tom_tat_promo["UNVERIFIABLE"]
tom_tat_promo["TY_LE_HOP_LE_%"] = (tom_tat_promo["HOP_LE"] / tom_tat_promo["TONG"] * 100).round(2)
tom_tat_promo.columns.name = None

tom_tat_promo.to_csv(DOCS_DIR / "promotion_category_summary.csv", index=False, encoding="utf-8-sig")
print(f"[OK] Luu bao cao KT6c tong tat : docs/promotion_category_summary.csv ({len(tom_tat_promo)} ma promo)")

print("\nTONG KET PHAN LOAI GIAO DICH KT6c:")
for k, v in giao_dich["ket_qua_kiem_tra"].value_counts().items():
    print(f"  {k:<16}: {v:,} ({v/len(giao_dich)*100:.2f}%)")

# =============================================================================
# TONG KET KT8
# =============================================================================
print(f"\n{SEP}"); print("TONG KET KT8"); print(SEP)
dem = df_report["Trang_thai"].value_counts()
print(f"""SO MUC KIEM TRA THEO TRANG THAI:
{dem.to_string()}

Chi giai thich:
  DAT        : Khong phat hien van de
  NGHI_VAN   : Can xem xet voi chu du an truoc khi ket luan la loi
  LOI        : Vi pham rang buoc co so / nghiep vu chac chan

[GHI CHU] KT8 chi KIEM TRA, khong thuc hien sua doi du lieu.
          Du lieu goc trong data/raw/ duoc giu nguyen 100%%.
""")
