"""
KT8 - Kiem tra kieu du lieu va gia tri bat thuong
Fashion_DW_Project

Pham vi: 13 file CSV nghiep vu (bo qua 2 file submission du bao)
  customers, geography, inventory, order_items, orders, payments,
  products, promotions, returns, reviews, sales, shipments, web_traffic

Nguyen tac:
  - Chi kiem tra va phan loai. Khong sua, khong xoa, khong them du lieu.
  - Du lieu trong data/raw/ duoc giu nguyen 100%.
  - Phan biet LOI (vi pham quy tac chac chan) voi
    NGHI_VAN (can xem xet nghiep vu truoc khi ket luan).

Ket qua xuat ra:
  docs/value_validation_report.csv   -- tong hop tung muc kiem tra
  docs/value_validation_issues.csv   -- danh sach ban ghi cu the co van de

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

# ─── Bo tich luy ket qua ──────────────────────────────────────────────────────
report_rows = []   # Tong hop theo tung muc kiem tra
issue_rows  = []   # Danh sach ban ghi co van de cu the

def log(ma, bang, kiem_tra, mo_ta, so_van_de, tong, trang_thai, ghi_chu):
    """Ghi mot dong vao bang tong hop."""
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
        tmp.insert(0, "_bang",      bang)
        tmp.insert(1, "_ma_kt",     ma_kt)
        tmp.insert(2, "_van_de",    mo_ta_van_de)
        issue_rows.append(tmp)

def st(so_van_de, muc="LOI"):
    """Tra ve trang_thai dua tren so luong van de."""
    return muc if so_van_de > 0 else "DAT"

# ─── Nap du lieu ──────────────────────────────────────────────────────────────
print("Dang nap du lieu...")
customers  = pd.read_csv(RAW_DIR / "customers.csv",   low_memory=False,
                         parse_dates=["signup_date"])
geography  = pd.read_csv(RAW_DIR / "geography.csv",   low_memory=False)
inventory  = pd.read_csv(RAW_DIR / "inventory.csv",   low_memory=False,
                         parse_dates=["snapshot_date"])
order_items= pd.read_csv(RAW_DIR / "order_items.csv", low_memory=False)
orders     = pd.read_csv(RAW_DIR / "orders.csv",      low_memory=False,
                         parse_dates=["order_date"])
payments   = pd.read_csv(RAW_DIR / "payments.csv",    low_memory=False)
products   = pd.read_csv(RAW_DIR / "products.csv",    low_memory=False)
promotions = pd.read_csv(RAW_DIR / "promotions.csv",  low_memory=False,
                         parse_dates=["start_date", "end_date"])
returns    = pd.read_csv(RAW_DIR / "returns.csv",     low_memory=False,
                         parse_dates=["return_date"])
reviews    = pd.read_csv(RAW_DIR / "reviews.csv",     low_memory=False,
                         parse_dates=["review_date"])
sales      = pd.read_csv(RAW_DIR / "sales.csv",       low_memory=False,
                         parse_dates=["Date"])
shipments  = pd.read_csv(RAW_DIR / "shipments.csv",   low_memory=False,
                         parse_dates=["ship_date", "delivery_date"])
web        = pd.read_csv(RAW_DIR / "web_traffic.csv", low_memory=False,
                         parse_dates=["date"])

print("Nap xong. Bat dau KT8...\n")

# =============================================================================
# PHAN 1 — CUSTOMERS
# =============================================================================
print(SEP); print("PHAN 1: customers.csv"); print(SEP)
n = len(customers)

# 1.1 Kieu du lieu ngay signup_date
parse_fail = customers["signup_date"].isna().sum()
print(f"[1.1] signup_date parse fail: {parse_fail}")
log("1.1","customers","DTYPE_DATE","signup_date parse errors",
    parse_fail, n, st(parse_fail), "Kiem tra dinh dang ngay")

# 1.2 Gia tri tuong lai
future = (customers["signup_date"] > pd.Timestamp.now()).sum()
print(f"[1.2] signup_date in future: {future}")
log("1.2","customers","VALUE_FUTURE","signup_date > today",
    future, n, st(future), "Khach hang chua the dang ky trong tuong lai")

# 1.3 gender: gia tri hop le
valid_gender = {"Male","Female","Non-binary"}
bad_gender = (~customers["gender"].isin(valid_gender)).sum()
print(f"[1.3] gender ngoai tap hop hop le: {bad_gender}")
log("1.3","customers","VALUE_ENUM","gender invalid",
    bad_gender, n, st(bad_gender), f"Gia tri hop le: {valid_gender}")

# 1.4 age_group: gia tri hop le
valid_age = {"18-24","25-34","35-44","45-54","55+"}
bad_age = (~customers["age_group"].isin(valid_age)).sum()
print(f"[1.4] age_group ngoai tap hop hop le: {bad_age}")
log("1.4","customers","VALUE_ENUM","age_group invalid",
    bad_age, n, st(bad_age), f"Gia tri hop le: {valid_age}")

# 1.5 acquisition_channel: gia tri hop le
valid_ch = {"direct","email_campaign","organic_search","paid_search","referral","social_media"}
bad_ch = (~customers["acquisition_channel"].isin(valid_ch)).sum()
print(f"[1.5] acquisition_channel ngoai tap hop: {bad_ch}")
log("1.5","customers","VALUE_ENUM","acquisition_channel invalid",
    bad_ch, n, st(bad_ch), f"Gia tri hop le: {valid_ch}")

# =============================================================================
# PHAN 2 — GEOGRAPHY
# =============================================================================
print(f"\n{SEP}"); print("PHAN 2: geography.csv"); print(SEP)
n = len(geography)

# 2.1 zip am hoac bang 0
bad_zip = (geography["zip"] <= 0).sum()
print(f"[2.1] zip <= 0: {bad_zip}")
log("2.1","geography","VALUE_RANGE","zip <= 0",
    bad_zip, n, st(bad_zip), "Ma buu chinh phai la so duong")

# 2.2 region: gia tri hop le
valid_region = set(geography["region"].dropna().unique())
print(f"[2.2] geography.region distinct: {sorted(valid_region)}")
log("2.2","geography","VALUE_ENUM","region distinct values",
    0, n, "DAT", f"Distinct: {sorted(valid_region)}")

# =============================================================================
# PHAN 3 — PRODUCTS
# =============================================================================
print(f"\n{SEP}"); print("PHAN 3: products.csv"); print(SEP)
n = len(products)

# 3.1 price <= 0
bad_price = (products["price"] <= 0).sum()
print(f"[3.1] price <= 0: {bad_price}")
log("3.1","products","VALUE_RANGE","price <= 0",
    bad_price, n, st(bad_price), "Gia ban phai duong")

# 3.2 cogs <= 0
bad_cogs = (products["cogs"] <= 0).sum()
print(f"[3.2] cogs <= 0: {bad_cogs}")
log("3.2","products","VALUE_RANGE","cogs <= 0",
    bad_cogs, n, st(bad_cogs), "Gia von phai duong")

# 3.3 cogs > price (ban duoi gia von — loi chac chan)
cogs_over = products["cogs"] > products["price"]
print(f"[3.3] cogs > price: {cogs_over.sum()}")
log("3.3","products","LOGIC","cogs > price",
    cogs_over.sum(), n, st(cogs_over.sum()),
    "Ban duoi gia von la bat thuong nghiep vu")
save_issues(products[cogs_over], "products", "3.3", "cogs > price")

# 3.4 gross margin phan bo
margin = (products["price"] - products["cogs"]) / products["price"] * 100
low_margin = (margin < 5).sum()
print(f"[3.4] gross margin < 5%%: {low_margin}")
log("3.4","products","VALUE_RANGE","gross_margin < 5%",
    low_margin, n, st(low_margin, "NGHI_VAN"),
    "Bien lai thap bat thuong, can xem xet nghiep vu")

# 3.5 category hop le
valid_cat = {"Casual","GenZ","Outdoor","Streetwear"}
bad_cat = (~products["category"].isin(valid_cat)).sum()
print(f"[3.5] category ngoai tap hop: {bad_cat}")
log("3.5","products","VALUE_ENUM","category invalid",
    bad_cat, n, st(bad_cat), f"Gia tri hop le: {valid_cat}")

# =============================================================================
# PHAN 4 — PROMOTIONS
# =============================================================================
print(f"\n{SEP}"); print("PHAN 4: promotions.csv"); print(SEP)
n = len(promotions)

# 4.1 discount_value < 0
bad_dv = (promotions["discount_value"] < 0).sum()
print(f"[4.1] discount_value < 0: {bad_dv}")
log("4.1","promotions","VALUE_RANGE","discount_value < 0",
    bad_dv, n, st(bad_dv), "Muc giam gia khong the am")

# 4.2 percentage discount_value > 100
pct_mask = promotions["promo_type"] == "percentage"
pct_over = (pct_mask & (promotions["discount_value"] > 100)).sum()
print(f"[4.2] percentage discount_value > 100: {pct_over}")
log("4.2","promotions","VALUE_RANGE","pct discount_value > 100%",
    pct_over, pct_mask.sum(), st(pct_over),
    "Giam gia phan tram khong the vuot 100%")

# 4.3 end_date < start_date
invalid_dates = (promotions["end_date"] < promotions["start_date"]).sum()
print(f"[4.3] end_date < start_date: {invalid_dates}")
log("4.3","promotions","TIME_ORDER","end_date < start_date",
    invalid_dates, n, st(invalid_dates),
    "Ngay ket thuc phai sau ngay bat dau")
bad_promo_dates = promotions[promotions["end_date"] < promotions["start_date"]]
save_issues(bad_promo_dates, "promotions", "4.3", "end_date < start_date")

# 4.4 stackable_flag: chi nhan 0 hoac 1
bad_flag = (~promotions["stackable_flag"].isin([0, 1])).sum()
print(f"[4.4] stackable_flag ngoai [0,1]: {bad_flag}")
log("4.4","promotions","VALUE_ENUM","stackable_flag not in {0,1}",
    bad_flag, n, st(bad_flag), "Flag phai la 0 hoac 1")

# 4.5 min_order_value < 0
bad_mov = (promotions["min_order_value"] < 0).sum()
print(f"[4.5] min_order_value < 0: {bad_mov}")
log("4.5","promotions","VALUE_RANGE","min_order_value < 0",
    bad_mov, n, st(bad_mov), "Nguong don hang toi thieu khong the am")

# =============================================================================
# PHAN 5 — ORDERS
# =============================================================================
print(f"\n{SEP}"); print("PHAN 5: orders.csv"); print(SEP)
n = len(orders)

# 5.1 order_date parse fail
od_fail = orders["order_date"].isna().sum()
print(f"[5.1] order_date parse fail: {od_fail}")
log("5.1","orders","DTYPE_DATE","order_date parse errors",
    od_fail, n, st(od_fail), "Kiem tra dinh dang ngay")

# 5.2 order_date trong tuong lai
future_od = (orders["order_date"] > pd.Timestamp.now()).sum()
print(f"[5.2] order_date in future: {future_od}")
log("5.2","orders","VALUE_FUTURE","order_date > today",
    future_od, n, st(future_od), "Don hang khong the o tuong lai")

# 5.3 order_status hop le
valid_status = {"created","paid","shipped","delivered","returned","cancelled"}
bad_status = (~orders["order_status"].isin(valid_status)).sum()
print(f"[5.3] order_status ngoai tap hop: {bad_status}")
log("5.3","orders","VALUE_ENUM","order_status invalid",
    bad_status, n, st(bad_status), f"Gia tri hop le: {valid_status}")

# 5.4 payment_method hop le
valid_pm = {"credit_card","cod","paypal","bank_transfer","apple_pay"}
bad_pm = (~orders["payment_method"].isin(valid_pm)).sum()
print(f"[5.4] payment_method ngoai tap hop: {bad_pm}")
log("5.4","orders","VALUE_ENUM","payment_method invalid",
    bad_pm, n, st(bad_pm), f"Gia tri hop le: {valid_pm}")

# 5.5 device_type hop le
valid_dev = {"desktop","mobile","tablet"}
bad_dev = (~orders["device_type"].isin(valid_dev)).sum()
print(f"[5.5] device_type ngoai tap hop: {bad_dev}")
log("5.5","orders","VALUE_ENUM","device_type invalid",
    bad_dev, n, st(bad_dev), f"Gia tri hop le: {valid_dev}")

# 5.6 order_date < customer signup_date
# GHI CHU: Trong du lieu nay, signup_date phan anh ngay cap nhat ho so
#          hoac ngay dang ky chuong trinh khach hang than thiet,
#          KHONG nhat thiet la lan dau tien khach hang mua hang.
#          Do do day la NGHI_VAN, khong phai LOI chac chan.
merged_co = orders[["order_id","customer_id","order_date"]].merge(
    customers[["customer_id","signup_date"]], on="customer_id", how="left")
before_signup = merged_co["order_date"] < merged_co["signup_date"]
n_before = before_signup.sum()
print(f"[5.6] order_date < customer signup_date: {n_before} "
      f"({n_before/n*100:.2f}%) — xem ghi chu")
log("5.6","orders","TIME_ORDER",
    "order_date < customer signup_date",
    n_before, n, "NGHI_VAN" if n_before > 0 else "DAT",
    "signup_date co the la ngay cap nhat ho so, khong phai ngay dang ky lan dau. "
    "Ti le 73.7% cho thay day la dac trung du lieu, can xac minh voi chu du an.")
save_issues(
    merged_co[before_signup].head(500),   # cap 500 dong mau de tranh file qua lon
    "orders", "5.6",
    "order_date < signup_date (500-row sample)")

# =============================================================================
# PHAN 6 — ORDER ITEMS
# =============================================================================
print(f"\n{SEP}"); print("PHAN 6: order_items.csv"); print(SEP)
n = len(order_items)

# 6.1 quantity <= 0
bad_qty = (order_items["quantity"] <= 0).sum()
print(f"[6.1] quantity <= 0: {bad_qty}")
log("6.1","order_items","VALUE_RANGE","quantity <= 0",
    bad_qty, n, st(bad_qty), "So luong phai la so nguyen duong")

# 6.2 unit_price <= 0
bad_up = (order_items["unit_price"] <= 0).sum()
print(f"[6.2] unit_price <= 0: {bad_up}")
log("6.2","order_items","VALUE_RANGE","unit_price <= 0",
    bad_up, n, st(bad_up), "Don gia phai duong")

# 6.3 discount_amount < 0
bad_da = (order_items["discount_amount"] < 0).sum()
print(f"[6.3] discount_amount < 0: {bad_da}")
log("6.3","order_items","VALUE_RANGE","discount_amount < 0",
    bad_da, n, st(bad_da), "Giam gia khong the am")

# 6.4 discount_amount > unit_price * quantity
order_items = order_items.assign(
    _total=order_items["unit_price"] * order_items["quantity"]
)
discount_over = order_items["discount_amount"] > order_items["_total"]
n_dov = discount_over.sum()
print(f"[6.4] discount_amount > unit_price*quantity: {n_dov}")
log("6.4","order_items","LOGIC","discount_amount > total_line_value",
    n_dov, n, st(n_dov),
    "Giam gia khong the lon hon gia tri dong hang")
save_issues(order_items[discount_over].drop(columns=["_total"]),
            "order_items", "6.4", "discount_amount > total line value")

# 6.5 promo_id co gia tri nhung discount_amount = 0
promo_no_discount = (order_items["promo_id"].notna() &
                     (order_items["discount_amount"] == 0)).sum()
print(f"[6.5] promo_id co gia tri nhung discount_amount=0: {promo_no_discount}")
log("6.5","order_items","LOGIC","promo_id set but discount=0",
    promo_no_discount, n, st(promo_no_discount, "NGHI_VAN"),
    "Co the la KM ngoai thi truong (free shipping) nhung can xac nhan")

# 6.6 Khong co promo nhung co discount
no_promo_has_discount = (order_items["promo_id"].isna() &
                         order_items["promo_id_2"].isna() &
                         (order_items["discount_amount"] > 0)).sum()
print(f"[6.6] khong co promo nhung discount_amount > 0: {no_promo_has_discount}")
log("6.6","order_items","LOGIC","no promo_id but discount_amount > 0",
    no_promo_has_discount, n, st(no_promo_has_discount, "NGHI_VAN"),
    "Can xac nhan: co the la giam gia tho cong hoac thieu promo_id")

order_items = order_items.drop(columns=["_total"])

# =============================================================================
# PHAN 7 — PAYMENTS
# =============================================================================
print(f"\n{SEP}"); print("PHAN 7: payments.csv"); print(SEP)
n = len(payments)

# 7.1 payment_value <= 0
bad_pv = (payments["payment_value"] <= 0).sum()
print(f"[7.1] payment_value <= 0: {bad_pv}")
log("7.1","payments","VALUE_RANGE","payment_value <= 0",
    bad_pv, n, st(bad_pv), "Gia tri thanh toan phai duong")

# 7.2 installments ngoai gia tri hop le
valid_inst = {1, 2, 3, 6, 12}
bad_inst = (~payments["installments"].isin(valid_inst)).sum()
print(f"[7.2] installments ngoai {valid_inst}: {bad_inst}")
log("7.2","payments","VALUE_ENUM","installments invalid",
    bad_inst, n, st(bad_inst, "NGHI_VAN"),
    f"Gia tri quan sat: {sorted(payments['installments'].unique())} "
    f"— xac nhan chinh sach tra gop")

# 7.3 payment_value vs tong order_items (kiem tra tinh nhat quan)
oi_total = (
    order_items
    .assign(_total=order_items["unit_price"]*order_items["quantity"]
                   - order_items["discount_amount"])
    .groupby("order_id")["_total"].sum()
    .reset_index(name="computed_total")
)
merged_pay = payments.merge(oi_total, on="order_id", how="inner")
diff = (merged_pay["payment_value"] - merged_pay["computed_total"]).abs()
n_diff = (diff > 0.01).sum()
print(f"[7.3] payment_value khac computed total > 0.01: {n_diff}  max_diff={diff.max():.4f}")
log("7.3","payments","LOGIC","payment_value != sum(line_totals)",
    n_diff, len(merged_pay), st(n_diff),
    "Gia tri thanh toan phai khop voi tong dong hang sau giam gia")

# =============================================================================
# PHAN 8 — SHIPMENTS
# =============================================================================
print(f"\n{SEP}"); print("PHAN 8: shipments.csv"); print(SEP)
n = len(shipments)

# 8.1 ship_date parse fail
sd_fail = shipments["ship_date"].isna().sum()
print(f"[8.1] ship_date parse fail: {sd_fail}")
log("8.1","shipments","DTYPE_DATE","ship_date parse errors", sd_fail, n, st(sd_fail), "")

# 8.2 delivery_date parse fail
dd_fail = shipments["delivery_date"].isna().sum()
print(f"[8.2] delivery_date parse fail: {dd_fail}")
log("8.2","shipments","DTYPE_DATE","delivery_date parse errors", dd_fail, n, st(dd_fail), "")

# 8.3 delivery_date < ship_date
del_before_ship = (shipments["delivery_date"] < shipments["ship_date"]).sum()
print(f"[8.3] delivery_date < ship_date: {del_before_ship}")
log("8.3","shipments","TIME_ORDER","delivery_date < ship_date",
    del_before_ship, n, st(del_before_ship),
    "Khong the giao hang truoc khi xuat kho")
save_issues(shipments[shipments["delivery_date"] < shipments["ship_date"]],
            "shipments", "8.3", "delivery_date < ship_date")

# 8.4 ship_date < order_date
merged_ship = shipments.merge(
    orders[["order_id","order_date"]], on="order_id", how="inner")
ship_before_order = (merged_ship["ship_date"] < merged_ship["order_date"]).sum()
print(f"[8.4] ship_date < order_date: {ship_before_order}")
log("8.4","shipments","TIME_ORDER","ship_date < order_date",
    ship_before_order, len(merged_ship), st(ship_before_order),
    "Khong the xuat kho truoc khi dat hang")
save_issues(merged_ship[merged_ship["ship_date"] < merged_ship["order_date"]],
            "shipments", "8.4", "ship_date < order_date")

# 8.5 shipping_fee < 0
bad_fee = (shipments["shipping_fee"] < 0).sum()
print(f"[8.5] shipping_fee < 0: {bad_fee}")
log("8.5","shipments","VALUE_RANGE","shipping_fee < 0",
    bad_fee, n, st(bad_fee), "Phi van chuyen khong the am")

# 8.6 shipping_fee = 0 (nghi van — co the la mien phi van chuyen)
zero_fee = (shipments["shipping_fee"] == 0).sum()
print(f"[8.6] shipping_fee = 0: {zero_fee} ({zero_fee/n*100:.2f}%)")
log("8.6","shipments","VALUE_ZERO","shipping_fee = 0",
    zero_fee, n, "NGHI_VAN" if zero_fee > 0 else "DAT",
    "Co the la chinh sach mien phi van chuyen, can xac nhan")

# =============================================================================
# PHAN 9 — RETURNS
# =============================================================================
print(f"\n{SEP}"); print("PHAN 9: returns.csv"); print(SEP)
n = len(returns)

# 9.1 return_date parse fail
rd_fail = returns["return_date"].isna().sum()
print(f"[9.1] return_date parse fail: {rd_fail}")
log("9.1","returns","DTYPE_DATE","return_date parse errors", rd_fail, n, st(rd_fail), "")

# 9.2 return_date < order_date
merged_ret = returns.merge(
    orders[["order_id","order_date"]], on="order_id", how="left")
ret_before_order = (merged_ret["return_date"] < merged_ret["order_date"]).sum()
print(f"[9.2] return_date < order_date: {ret_before_order}")
log("9.2","returns","TIME_ORDER","return_date < order_date",
    ret_before_order, n, st(ret_before_order),
    "Khong the tra hang truoc khi dat hang")
save_issues(merged_ret[merged_ret["return_date"] < merged_ret["order_date"]],
            "returns", "9.2", "return_date < order_date")

# 9.3 return_quantity <= 0
bad_rq = (returns["return_quantity"] <= 0).sum()
print(f"[9.3] return_quantity <= 0: {bad_rq}")
log("9.3","returns","VALUE_RANGE","return_quantity <= 0",
    bad_rq, n, st(bad_rq), "So luong tra hang phai duong")

# 9.4 return_quantity > so luong da mua (tong hop theo order_id, product_id)
# Luu y: Mot don hang co the co nhieu dong cung product_id (vi du order 698128, sp 1009),
# do do can tong hop quantity theo (order_id, product_id) truoc khi so sanh de tranh false positive.
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
n_over = over_return.sum()
print(f"[9.4] return_quantity > bought_quantity: {n_over}")
log("9.4","returns","LOGIC","return_quantity > bought_quantity",
    n_over, n, st(n_over),
    "Tong so luong tra khong the vuot tong so luong da mua")
if n_over > 0:
    save_issues(
        merged_rq[over_return][["order_id","product_id",
                                "total_returned_qty","bought_qty"]],
        "returns", "9.4", "return_quantity > bought_quantity")

# 9.5 refund_amount <= 0
bad_ref = (returns["refund_amount"] <= 0).sum()
print(f"[9.5] refund_amount <= 0: {bad_ref}")
log("9.5","returns","VALUE_RANGE","refund_amount <= 0",
    bad_ref, n, st(bad_ref), "So tien hoan tra phai duong")

# 9.6 return_reason hop le
valid_rr = {"changed_mind","defective","late_delivery","not_as_described","wrong_size"}
bad_rr = (~returns["return_reason"].isin(valid_rr)).sum()
print(f"[9.6] return_reason ngoai tap hop: {bad_rr}")
log("9.6","returns","VALUE_ENUM","return_reason invalid",
    bad_rr, n, st(bad_rr), f"Gia tri hop le: {valid_rr}")

# =============================================================================
# PHAN 10 — REVIEWS
# =============================================================================
print(f"\n{SEP}"); print("PHAN 10: reviews.csv"); print(SEP)
n = len(reviews)

# 10.1 rating ngoai [1, 5]
bad_rating = (~reviews["rating"].between(1, 5)).sum()
print(f"[10.1] rating ngoai [1,5]: {bad_rating}")
log("10.1","reviews","VALUE_RANGE","rating not in [1,5]",
    bad_rating, n, st(bad_rating), "Rating phai tu 1 den 5")

# 10.2 review_date < order_date
merged_rv = reviews.merge(
    orders[["order_id","order_date"]], on="order_id", how="left")
rv_before_order = (merged_rv["review_date"] < merged_rv["order_date"]).sum()
print(f"[10.2] review_date < order_date: {rv_before_order}")
log("10.2","reviews","TIME_ORDER","review_date < order_date",
    rv_before_order, n, st(rv_before_order),
    "Khong the danh gia truoc khi dat hang")
save_issues(merged_rv[merged_rv["review_date"] < merged_rv["order_date"]],
            "reviews", "10.2", "review_date < order_date")

# 10.3 review_date < delivery_date (co the danh gia truoc khi nhan hang)
merged_rv_d = reviews.merge(
    shipments[["order_id","delivery_date"]], on="order_id", how="left")
rv_before_del = (merged_rv_d["review_date"] < merged_rv_d["delivery_date"]).sum()
print(f"[10.3] review_date < delivery_date: {rv_before_del} (nghi van)")
log("10.3","reviews","TIME_ORDER","review_date < delivery_date",
    rv_before_del, merged_rv_d["delivery_date"].notna().sum(),
    "NGHI_VAN" if rv_before_del > 0 else "DAT",
    "Mot so he thong cho phep danh gia ngay sau khi dat hang; "
    "can xac nhan chinh sach cua san")

# =============================================================================
# PHAN 11 — INVENTORY
# =============================================================================
print(f"\n{SEP}"); print("PHAN 11: inventory.csv"); print(SEP)
n = len(inventory)

# 11.1 stock_on_hand < 0
bad_soh = (inventory["stock_on_hand"] < 0).sum()
print(f"[11.1] stock_on_hand < 0: {bad_soh}")
log("11.1","inventory","VALUE_RANGE","stock_on_hand < 0",
    bad_soh, n, st(bad_soh), "Ton kho khong the am")

# 11.2 fill_rate ngoai [0, 1]
bad_fr = (~inventory["fill_rate"].between(0, 1)).sum()
print(f"[11.2] fill_rate ngoai [0,1]: {bad_fr}")
log("11.2","inventory","VALUE_RANGE","fill_rate not in [0,1]",
    bad_fr, n, st(bad_fr), "Fill rate la ty le, phai trong [0,1]")

# 11.3 sell_through_rate ngoai [0, 1]
bad_str = (~inventory["sell_through_rate"].between(0, 1)).sum()
print(f"[11.3] sell_through_rate ngoai [0,1]: {bad_str}")
log("11.3","inventory","VALUE_RANGE","sell_through_rate not in [0,1]",
    bad_str, n, st(bad_str), "Sell-through rate la ty le, phai trong [0,1]")

# 11.4 reorder_flag luon = 0 (nghi van — co the la loi hoac chinh sach du lieu)
all_zero_reorder = (inventory["reorder_flag"] == 0).all()
print(f"[11.4] reorder_flag luon = 0: {all_zero_reorder} => NGHI_VAN")
log("11.4","inventory","VALUE_CONST","reorder_flag always 0",
    1 if all_zero_reorder else 0, 1, "NGHI_VAN" if all_zero_reorder else "DAT",
    "reorder_flag luon bang 0 tren toan bo 60,247 ban ghi — "
    "co the do logic tai tao du lieu hoac chinh sach kho chua duoc kich hoat")

# 11.5 stockout_flag ngoai [0,1]
bad_sf = (~inventory["stockout_flag"].isin([0,1])).sum()
print(f"[11.5] stockout_flag ngoai [0,1]: {bad_sf}")
log("11.5","inventory","VALUE_ENUM","stockout_flag not in {0,1}",
    bad_sf, n, st(bad_sf), "Flag phai la 0 hoac 1")

# 11.6 overstock_flag ngoai [0,1]
bad_of = (~inventory["overstock_flag"].isin([0,1])).sum()
print(f"[11.6] overstock_flag ngoai [0,1]: {bad_of}")
log("11.6","inventory","VALUE_ENUM","overstock_flag not in {0,1}",
    bad_of, n, st(bad_of), "Flag phai la 0 hoac 1")

# 11.7 units_sold < 0
bad_us = (inventory["units_sold"] < 0).sum()
print(f"[11.7] units_sold < 0: {bad_us}")
log("11.7","inventory","VALUE_RANGE","units_sold < 0",
    bad_us, n, st(bad_us), "So luong ban khong the am")

# =============================================================================
# PHAN 12 — SALES (du lieu tong hop theo ngay)
# =============================================================================
print(f"\n{SEP}"); print("PHAN 12: sales.csv"); print(SEP)
n = len(sales)

# 12.1 Revenue <= 0
bad_rev = (sales["Revenue"] <= 0).sum()
print(f"[12.1] Revenue <= 0: {bad_rev}")
log("12.1","sales","VALUE_RANGE","Revenue <= 0",
    bad_rev, n, st(bad_rev), "Doanh thu phai duong")

# 12.2 COGS <= 0
bad_cogs_s = (sales["COGS"] <= 0).sum()
print(f"[12.2] COGS <= 0: {bad_cogs_s}")
log("12.2","sales","VALUE_RANGE","COGS <= 0",
    bad_cogs_s, n, st(bad_cogs_s), "Chi phi von phai duong")

# 12.3 COGS > Revenue (ban lo — nghi van)
cogs_over_rev = (sales["COGS"] > sales["Revenue"]).sum()
print(f"[12.3] COGS > Revenue: {cogs_over_rev}")
log("12.3","sales","LOGIC","COGS > Revenue",
    cogs_over_rev, n, st(cogs_over_rev, "NGHI_VAN"),
    "Ban lo tren tong hop ngay — can xac nhan voi don vi nghiep vu")
save_issues(sales[sales["COGS"] > sales["Revenue"]],
            "sales", "12.3", "COGS > Revenue (ban lo)")

# 12.4 Date trung lap
dup_date = sales["Date"].duplicated().sum()
print(f"[12.4] Date trung lap: {dup_date}")
log("12.4","sales","DUPLICATE","Date duplicated",
    dup_date, n, st(dup_date), "Moi ngay chi co 1 ban ghi tong hop")

# =============================================================================
# PHAN 13 — WEB TRAFFIC
# =============================================================================
print(f"\n{SEP}"); print("PHAN 13: web_traffic.csv"); print(SEP)
n = len(web)

# 13.1 sessions < unique_visitors (bat thuong logic)
sess_lt_uv = (web["sessions"] < web["unique_visitors"]).sum()
print(f"[13.1] sessions < unique_visitors: {sess_lt_uv}")
log("13.1","web_traffic","LOGIC","sessions < unique_visitors",
    sess_lt_uv, n, st(sess_lt_uv, "NGHI_VAN"),
    "Mot nguoi co the tao nhieu phien; sessions thuong >= unique_visitors")

# 13.2 bounce_rate ngoai [0, 1]
bad_br = (~web["bounce_rate"].between(0, 1)).sum()
print(f"[13.2] bounce_rate ngoai [0,1]: {bad_br}")
log("13.2","web_traffic","VALUE_RANGE","bounce_rate not in [0,1]",
    bad_br, n, st(bad_br), "Ty le bounce phai trong [0,1]")

# 13.3 avg_session_duration_sec < 0
bad_dur = (web["avg_session_duration_sec"] < 0).sum()
print(f"[13.3] avg_session_duration_sec < 0: {bad_dur}")
log("13.3","web_traffic","VALUE_RANGE","avg_session_duration_sec < 0",
    bad_dur, n, st(bad_dur), "Thoi gian phien khong the am")

# 13.4 date trung lap
dup_wdate = web["date"].duplicated().sum()
print(f"[13.4] date trung lap: {dup_wdate}")
log("13.4","web_traffic","DUPLICATE","date duplicated",
    dup_wdate, n, st(dup_wdate, "NGHI_VAN"),
    "Co the co nhieu dong/nguon traffic cung ngay — kiem tra traffic_source")

# 13.5 page_views < sessions (bat thuong logic)
pv_lt_sess = (web["page_views"] < web["sessions"]).sum()
print(f"[13.5] page_views < sessions: {pv_lt_sess}")
log("13.5","web_traffic","LOGIC","page_views < sessions",
    pv_lt_sess, n, st(pv_lt_sess, "NGHI_VAN"),
    "Trung binh page_views/session phai >= 1")

# =============================================================================
# XUAT KET QUA
# =============================================================================
print(f"\n{SEP}"); print("XUAT KET QUA"); print(SEP)

df_report = pd.DataFrame(report_rows)
report_path = DOCS_DIR / "value_validation_report.csv"
df_report.to_csv(report_path, index=False, encoding="utf-8-sig")
print(f"[OK] Bao cao tong hop : {report_path}  ({len(df_report)} muc)")

issues_path = DOCS_DIR / "value_validation_issues.csv"
if issue_rows:
    df_issues = pd.concat(issue_rows, ignore_index=True)
    df_issues.to_csv(issues_path, index=False, encoding="utf-8-sig")
    print(f"[OK] Danh sach van de : {issues_path}  ({len(df_issues)} dong)")
else:
    pd.DataFrame().to_csv(issues_path, index=False, encoding="utf-8-sig")
    print(f"[OK] Khong co van de cu the. File rong: {issues_path}")

# =============================================================================
# TONG KET
# =============================================================================
print(f"\n{SEP}"); print("TONG KET KT8"); print(SEP)

dem = df_report["Trang_thai"].value_counts()
print(df_report[["Ma_KT","Bang","Ten_KT","So_van_de","Tong_KT",
                 "Ty_le_%","Trang_thai"]].to_string(index=False))

print(f"""
SO MUC KIEM TRA THEO TRANG THAI:
{dem.to_string()}

Chi giai thich:
  DAT        : Khong phat hien van de
  NGHI_VAN   : Can xem xet voi chu du an truoc khi ket luan la loi
  LOI        : Vi pham rang buoc co so / nghiep vu chac chan

[GHI CHU] KT8 chi KIEM TRA, khong thuc hien sua doi du lieu.
          Du lieu goc trong data/raw/ duoc giu nguyen 100%%.
""")
