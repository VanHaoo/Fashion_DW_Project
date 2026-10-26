
from pathlib import Path
import pandas as pd

# Lay duong dan thu muc du an
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
DOCS_DIR = BASE_DIR / "docs"

# Tim tat ca file CSV
csv_files = sorted(RAW_DIR.glob("*.csv"))

print("TONG SO FILE CSV:", len(csv_files))
print("=" * 50)

for file in csv_files:
    df = pd.read_csv(file, low_memory=False)

    print(f"\nFILE: {file.name}")
    print(f"So dong: {df.shape[0]}")
    print(f"So cot: {df.shape[1]}")
    print(f"Gia tri thieu: {df.isnull().sum().sum()}")
    print(f"Dong trung hoan toan: {df.duplicated().sum()}")
    print("-" * 50)

# KIEM TRA CHI TIET CAC COT BI THIEU DU LIEU

print("\n===== CHI TIET GIA TRI THIEU =====")

for filename in ["order_items.csv", "promotions.csv"]:
    file_path = RAW_DIR / filename
    df = pd.read_csv(file_path, low_memory=False)

    print(f"\nFILE: {filename}")

    missing = df.isnull().sum()
    missing = missing[missing > 0]

    print(missing)

    print("\nTY LE THIEU (%):")
    print((missing / len(df) * 100).round(2))

    print("\n5 DONG DAU TIEN:")
    print(df.head().to_string(index=False))


# =============================================================
# KIEM TRA TINH NHAT QUAN DU LIEU KHUYEN MAI
# =============================================================

print("\n" + "=" * 60)
print("KIEM TRA TINH NHAT QUAN DU LIEU KHUYEN MAI")
print("=" * 60)

# Doc du lieu tu hai bang
oi = pd.read_csv(RAW_DIR / "order_items.csv", low_memory=False)
promo = pd.read_csv(RAW_DIR / "promotions.csv", low_memory=False)

tong_dong = len(oi)
print(f"\nTong so ban ghi order_items: {tong_dong:,}")
print(f"Tong so promo_id hop le trong promotions: {promo['promo_id'].nunique()}")

# -----------------------------------------------------------
# KIEM TRA 1: Co promo_id nhung discount_amount = 0
# -----------------------------------------------------------
co_promo_discount_zero = oi[oi["promo_id"].notna() & (oi["discount_amount"] == 0)]
so_luong_1 = len(co_promo_discount_zero)

print("\n" + "-" * 60)
print("[KT1] Co promo_id nhung discount_amount = 0")
print(f"  => So ban ghi: {so_luong_1:,}")
if so_luong_1 > 0:
    print("  => Phan tich:")
    print("     - Co the hop le: chuong trinh khuyen mai dang cho (pending),")
    print("       da het han truoc khi ap dung, hoac dat gia tri toi thieu.")
    print("     - Can kiem tra them: so sanh voi thoi gian dat hang,")
    print("       gia tri don hang va dieu kien ap dung cua promo do.")

# -----------------------------------------------------------
# KIEM TRA 2: Khong co promo_id va promo_id_2 nhung discount_amount > 0
# -----------------------------------------------------------
khong_promo_co_giam = oi[
    oi["promo_id"].isna()
    & oi["promo_id_2"].isna()
    & (oi["discount_amount"] > 0)
]
so_luong_2 = len(khong_promo_co_giam)

print("\n" + "-" * 60)
print("[KT2] Khong co promo_id VA promo_id_2 nhung discount_amount > 0")
print(f"  => So ban ghi: {so_luong_2:,}")
if so_luong_2 > 0:
    print("  => Phan tich:")
    print("     - Day la truong hop dang nghi van: giam gia nhung khong co ma khuyen mai.")
    print("     - Co the hop le: giam gia thu cong (manual discount) khong qua he thong promo,")
    print("       hoac giam gia theo loai khach hang VIP / hop dong dac biet.")
    print("     - Can kiem tra them: nguon goc cua giam gia nay co duoc ghi nhan o dau khong.")

# -----------------------------------------------------------
# KIEM TRA 3: Co promo_id_2 nhung thieu promo_id
# -----------------------------------------------------------
co_promo2_thieu_promo1 = oi[oi["promo_id_2"].notna() & oi["promo_id"].isna()]
so_luong_3 = len(co_promo2_thieu_promo1)

print("\n" + "-" * 60)
print("[KT3] Co promo_id_2 nhung thieu promo_id")
print(f"  => So ban ghi: {so_luong_3:,}")
if so_luong_3 > 0:
    print("  => Phan tich:")
    print("     - Thuong promo_id la khuyen mai chinh, promo_id_2 la phu (xep chong / stackable).")
    print("     - Viec co promo_id_2 ma khong co promo_id la bat thuong ve logic nghiep vu.")
    print("     - Can kiem tra them: co the la loi nhap lieu hoac promo_id bi xoa sau khi dat hang.")

# -----------------------------------------------------------
# KIEM TRA 4: promo_id va promo_id_2 co ton tai trong promotions hay khong
# -----------------------------------------------------------
valid_promo_ids = set(promo["promo_id"].dropna().unique())

# Kiem tra promo_id
mask_promo1_khong_hop_le = oi["promo_id"].notna() & ~oi["promo_id"].isin(valid_promo_ids)
so_luong_4a = mask_promo1_khong_hop_le.sum()

# Kiem tra promo_id_2
mask_promo2_khong_hop_le = oi["promo_id_2"].notna() & ~oi["promo_id_2"].isin(valid_promo_ids)
so_luong_4b = mask_promo2_khong_hop_le.sum()

print("\n" + "-" * 60)
print("[KT4] promo_id / promo_id_2 khong ton tai trong bang promotions")
print(f"  => promo_id khong hop le:   {so_luong_4a:,}")
print(f"  => promo_id_2 khong hop le: {so_luong_4b:,}")
if so_luong_4a > 0 or so_luong_4b > 0:
    print("  => Phan tich:")
    print("     - Cac ma khuyen mai khong ton tai trong bang promotions co the la loi tham chieu.")
    print("     - Co the hop le neu bang promotions chua day du (vi du: promo da bi xoa).")
    print("     - Can kiem tra them: lay danh sach cac promo_id la.")
if so_luong_4a > 0:
    print("     Cac promo_id la:", oi.loc[mask_promo1_khong_hop_le, "promo_id"].unique())
if so_luong_4b > 0:
    print("     Cac promo_id_2 la:", oi.loc[mask_promo2_khong_hop_le, "promo_id_2"].unique())

# -----------------------------------------------------------
# KIEM TRA 5: discount_amount am
# -----------------------------------------------------------
discount_am = oi[oi["discount_amount"] < 0]
so_luong_5 = len(discount_am)

print("\n" + "-" * 60)
print("[KT5] discount_amount co gia tri am")
print(f"  => So ban ghi: {so_luong_5:,}")
if so_luong_5 > 0:
    print("  => Phan tich:")
    print("     - Giam gia am ve mat nghiep vu la vo nghia (tuc la tinh them tien).")
    print("     - Day la truong hop can kiem tra ky: co the la loi nhap lieu.")
    print(f"     - Gia tri nho nhat: {oi['discount_amount'].min()}")
    print(f"     - Gia tri lon nhat trong nhom am: {discount_am['discount_amount'].max()}")
else:
    print("  => Khong co truong hop bat thuong.")

# -----------------------------------------------------------
# KIEM TRA 6: Thong ke NULL cua promo_id, promo_id_2, applicable_category
# -----------------------------------------------------------
print("\n" + "-" * 60)
print("[KT6] Thong ke NULL cua cac truong lien quan khuyen mai")

# NULL trong order_items
null_promo1 = oi["promo_id"].isna().sum()
null_promo2 = oi["promo_id_2"].isna().sum()

print(f"\n  [order_items.csv] (tong {tong_dong:,} ban ghi)")
print(f"  promo_id       NULL: {null_promo1:,} ({null_promo1/tong_dong*100:.2f}%)")
print(f"  promo_id_2     NULL: {null_promo2:,} ({null_promo2/tong_dong*100:.2f}%)")

# NULL trong promotions
null_cat = promo["applicable_category"].isna().sum()
tong_promo = len(promo)

print(f"\n  [promotions.csv] (tong {tong_promo:,} ban ghi)")
print(f"  applicable_category NULL: {null_cat:,} ({null_cat/tong_promo*100:.2f}%)")
print("  => Co the hop le: khuyen mai ap dung cho tat ca danh muc se de trong truong nay.")

# -----------------------------------------------------------
# TONG HOP KET QUA VA LUU BAO CAO
# -----------------------------------------------------------
print("\n" + "=" * 60)
print("TONG HOP KET QUA KIEM TRA KHUYEN MAI")
print("=" * 60)

ket_qua = [
    {
        "Ma_kiem_tra": "KT1",
        "Mo_ta": "Co promo_id nhung discount_amount = 0",
        "So_ban_ghi": so_luong_1,
        "Ty_le_%": round(so_luong_1 / tong_dong * 100, 4),
        "Danh_gia": (
            "Bat thuong - can kiem tra them" if so_luong_1 > 0 else "Binh thuong"
        ),
    },
    {
        "Ma_kiem_tra": "KT2",
        "Mo_ta": "Khong co promo nhung discount_amount > 0",
        "So_ban_ghi": so_luong_2,
        "Ty_le_%": round(so_luong_2 / tong_dong * 100, 4),
        "Danh_gia": (
            "Nghi van - can xac minh nguon goc giam gia" if so_luong_2 > 0 else "Binh thuong"
        ),
    },
    {
        "Ma_kiem_tra": "KT3",
        "Mo_ta": "Co promo_id_2 nhung thieu promo_id",
        "So_ban_ghi": so_luong_3,
        "Ty_le_%": round(so_luong_3 / tong_dong * 100, 4),
        "Danh_gia": (
            "Bat thuong ve logic - can kiem tra" if so_luong_3 > 0 else "Binh thuong"
        ),
    },
    {
        "Ma_kiem_tra": "KT4a",
        "Mo_ta": "promo_id khong ton tai trong promotions",
        "So_ban_ghi": so_luong_4a,
        "Ty_le_%": round(so_luong_4a / tong_dong * 100, 4),
        "Danh_gia": (
            "Loi tham chieu - can xac minh" if so_luong_4a > 0 else "Hop le"
        ),
    },
    {
        "Ma_kiem_tra": "KT4b",
        "Mo_ta": "promo_id_2 khong ton tai trong promotions",
        "So_ban_ghi": so_luong_4b,
        "Ty_le_%": round(so_luong_4b / tong_dong * 100, 4),
        "Danh_gia": (
            "Loi tham chieu - can xac minh" if so_luong_4b > 0 else "Hop le"
        ),
    },
    {
        "Ma_kiem_tra": "KT5",
        "Mo_ta": "discount_amount co gia tri am",
        "So_ban_ghi": so_luong_5,
        "Ty_le_%": round(so_luong_5 / tong_dong * 100, 4),
        "Danh_gia": (
            "Loi du lieu - can xu ly" if so_luong_5 > 0 else "Binh thuong"
        ),
    },
    {
        "Ma_kiem_tra": "KT6a",
        "Mo_ta": "NULL: order_items.promo_id",
        "So_ban_ghi": null_promo1,
        "Ty_le_%": round(null_promo1 / tong_dong * 100, 4),
        "Danh_gia": "Binh thuong - don hang khong ap khuyen mai",
    },
    {
        "Ma_kiem_tra": "KT6b",
        "Mo_ta": "NULL: order_items.promo_id_2",
        "So_ban_ghi": null_promo2,
        "Ty_le_%": round(null_promo2 / tong_dong * 100, 4),
        "Danh_gia": "Binh thuong - khong xep chong khuyen mai",
    },
    {
        "Ma_kiem_tra": "KT6c",
        "Mo_ta": "NULL: promotions.applicable_category",
        "So_ban_ghi": null_cat,
        "Ty_le_%": round(null_cat / tong_promo * 100, 4),
        "Danh_gia": "Co the hop le - khuyen mai cho tat ca danh muc",
    },
]

df_ket_qua = pd.DataFrame(ket_qua)
print(df_ket_qua.to_string(index=False))

# Luu bao cao ra file CSV
output_path = DOCS_DIR / "promotion_check_report.csv"
df_ket_qua.to_csv(output_path, index=False, encoding="utf-8-sig")
print(f"\n[OK] Da luu bao cao ket qua vao: {output_path}")
print("\n[GHI CHU] Day chi la buoc KIEM TRA. Chua thuc hien lam sach hoac sua du lieu.")


# =============================================================
# KIEM TRA KT6c CHI TIET: DANH MUC SAN PHAM VS APPLICABLE_CATEGORY
# Kiem tra 10 chuong trinh khuyen mai co applicable_category khac NULL
# =============================================================

print("\n" + "=" * 60)
print("KIEM TRA KT6c: NHAT QUAN DANH MUC SAN PHAM - KHUYEN MAI")
print("=" * 60)

# Doc products.csv
products = pd.read_csv(RAW_DIR / "products.csv", low_memory=False)

# Lay danh sach 10 promo co applicable_category khac NULL
promo_co_category = promo[promo["applicable_category"].notna()][
    ["promo_id", "applicable_category"]
].copy()
print(f"\nSo chuong trinh khuyen mai co applicable_category: {len(promo_co_category)}")
print(promo_co_category.to_string(index=False))

# Danh muc hop le tu bang products
print(f"\nCac danh muc san pham hien co trong products.csv: {sorted(products['category'].unique())}")

# Tao bang anh xa product_id -> category
product_category_map = products[["product_id", "category"]].drop_duplicates()

# -----------------------------------------------------------
# Tach rieng giao dich dung promo_id (chinh) va promo_id_2 (phu)
# -----------------------------------------------------------
def lay_giao_dich_theo_promo(df_oi, df_promo_cat, cot_promo, nhan_promo):
    """
    Lay cac dong order_items su dung promo thuoc nhom co applicable_category,
    gan them thong tin applicable_category tuong ung.
    """
    ket_hop = df_oi[df_oi[cot_promo].isin(df_promo_cat["promo_id"])][
        ["order_id", "product_id", "discount_amount", cot_promo]
    ].copy()
    ket_hop = ket_hop.rename(columns={cot_promo: "ma_promo_su_dung"})
    ket_hop["loai_promo"] = nhan_promo
    ket_hop = ket_hop.merge(
        df_promo_cat.rename(columns={"promo_id": "ma_promo_su_dung"}),
        on="ma_promo_su_dung",
        how="left",
    )
    return ket_hop


gd_promo1 = lay_giao_dich_theo_promo(oi, promo_co_category, "promo_id", "promo_id_chinh")
gd_promo2 = lay_giao_dich_theo_promo(oi, promo_co_category, "promo_id_2", "promo_id_phu")

# Gop lai
giao_dich = pd.concat([gd_promo1, gd_promo2], ignore_index=True)
tong_gd = len(giao_dich)

print(f"\nTong giao dich su dung promo co applicable_category: {tong_gd:,}")
print(f"  - Qua promo_id (chinh): {len(gd_promo1):,}")
print(f"  - Qua promo_id_2 (phu): {len(gd_promo2):,}")

# -----------------------------------------------------------
# Gan category san pham vao tung giao dich
# -----------------------------------------------------------
giao_dich = giao_dich.merge(
    product_category_map.rename(columns={"category": "product_category"}),
    on="product_id",
    how="left",
)

# -----------------------------------------------------------
# Phan loai tung giao dich
# -----------------------------------------------------------
def phan_loai(row):
    if pd.isna(row["product_category"]):
        # Khong tim thay product_id trong bang products
        return "UNVERIFIABLE"
    elif row["product_category"] == row["applicable_category"]:
        return "HOP_LE"
    else:
        return "REVIEW_REQUIRED"


giao_dich["ket_qua_kiem_tra"] = giao_dich.apply(phan_loai, axis=1)

# -----------------------------------------------------------
# Thong ke tong the
# -----------------------------------------------------------
thong_ke = giao_dich["ket_qua_kiem_tra"].value_counts()
so_hop_le = thong_ke.get("HOP_LE", 0)
so_review = thong_ke.get("REVIEW_REQUIRED", 0)
so_unverifiable = thong_ke.get("UNVERIFIABLE", 0)

print("\n" + "-" * 60)
print("TONG KET PHAN LOAI GIAO DICH:")
print(f"  HOP_LE           : {so_hop_le:,}  ({so_hop_le/tong_gd*100:.2f}%)")
print(f"  REVIEW_REQUIRED  : {so_review:,}  ({so_review/tong_gd*100:.2f}%)")
print(f"  UNVERIFIABLE     : {so_unverifiable:,}  ({so_unverifiable/tong_gd*100:.2f}%)")

# -----------------------------------------------------------
# Thong ke theo tung ma khuyen mai
# -----------------------------------------------------------
print("\n" + "-" * 60)
print("THONG KE THEO TUNG MA KHUYEN MAI:")

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

# Dam bao co day du cot (phong truong hop mot ket qua khong xuat hien)
for col in ["HOP_LE", "REVIEW_REQUIRED", "UNVERIFIABLE"]:
    if col not in tom_tat_promo.columns:
        tom_tat_promo[col] = 0

tom_tat_promo["TONG"] = (
    tom_tat_promo["HOP_LE"]
    + tom_tat_promo["REVIEW_REQUIRED"]
    + tom_tat_promo["UNVERIFIABLE"]
)
tom_tat_promo["TY_LE_HOP_LE_%"] = (
    tom_tat_promo["HOP_LE"] / tom_tat_promo["TONG"] * 100
).round(2)
tom_tat_promo.columns.name = None

print(tom_tat_promo.to_string(index=False))

# -----------------------------------------------------------
# Chi tiet cac giao dich REVIEW_REQUIRED (neu co)
# -----------------------------------------------------------
gd_review = giao_dich[giao_dich["ket_qua_kiem_tra"] == "REVIEW_REQUIRED"]
if len(gd_review) > 0:
    print("\n" + "-" * 60)
    print(f"CHI TIET GIAO DICH REVIEW_REQUIRED (hien thi toi da 10 dong):")
    print(gd_review[
        ["order_id", "product_id", "ma_promo_su_dung", "loai_promo",
         "applicable_category", "product_category", "discount_amount"]
    ].head(10).to_string(index=False))
    print("\n  => Phan tich: San pham trong giao dich nay thuoc danh muc khac voi")
    print("     applicable_category cua chuong trinh khuyen mai.")
    print("     Co the hop le: hang khuyen mai 'stackable' ap dung cho tat ca don co du dieu kien,")
    print("     hoac la loi gan ma khuyen mai sai san pham.")
    print("     De xuat: Kiem tra them dieu kien stackable_flag va min_order_value cua promo do.")
else:
    print("\n  => Khong co giao dich REVIEW_REQUIRED.")

# -----------------------------------------------------------
# Luu ket qua chi tiet ra file CSV
# -----------------------------------------------------------
output_validation_path = DOCS_DIR / "promotion_category_validation.csv"
giao_dich.to_csv(output_validation_path, index=False, encoding="utf-8-sig")
print(f"\n[OK] Da luu ket qua chi tiet vao: {output_validation_path}")

# Luu tom tat theo promo
output_summary_path = DOCS_DIR / "promotion_category_summary.csv"
tom_tat_promo.to_csv(output_summary_path, index=False, encoding="utf-8-sig")
print(f"[OK] Da luu tom tat theo promo vao: {output_summary_path}")

print("\n[GHI CHU] Buoc KT6c chi kiem tra va phan loai. Chua thuc hien chinh sua du lieu.")


