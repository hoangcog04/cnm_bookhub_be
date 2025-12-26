"""Seed script to populate provinces and wards from CSV file."""

import asyncio
import csv
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from cnm_bookhub_be.db.models import load_all_models
from cnm_bookhub_be.db.models.provinces import Province
from cnm_bookhub_be.db.models.wards import Ward
from cnm_bookhub_be.settings import settings


async def seed_locations() -> None:
    """Seed provinces and wards from CSV file."""
    # Load all models first
    load_all_models()

    # Create engine and session
    engine = create_async_engine(str(settings.db_url), echo=False)
    async_session = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )

    # Path to CSV file
    csv_file = Path(__file__).parent.parent.parent / "List_Wards.csv"
    
    if not csv_file.exists():
        print(f"❌ Error: CSV file not found at {csv_file}")  # noqa: T201
        return

    async with async_session() as session:
        try:
            # Read CSV and extract unique provinces
            provinces_dict = {}  # {code: full_name}
            wards_data = []
            
            print("📖 Reading CSV file...")  # noqa: T201
            with open(csv_file, "r", encoding="utf-8-sig") as f:  # utf-8-sig to handle BOM
                reader = csv.DictReader(f)
                
                # Debug: Print column names
                first_row = True
                
                for row in reader:
                    if first_row:
                        print(f"   CSV columns: {list(row.keys())}")  # noqa: T201
                        first_row = False
                    
                    # Strip whitespace from keys and values
                    row = {k.strip(): v.strip() for k, v in row.items()}
                    
                    province_code = row["Mã TP"]
                    province_name = row["Tỉnh / Thành Phố"]
                    ward_code = row["Mã"]
                    ward_name = row["Tên"]
                    
                    # Collect provinces
                    if province_code not in provinces_dict:
                        provinces_dict[province_code] = province_name
                    
                    # Collect wards
                    wards_data.append({
                        "code": ward_code,
                        "full_name": ward_name,
                        "province_code": province_code,
                    })
            
            print(f"✅ Found {len(provinces_dict)} provinces and {len(wards_data)} wards")  # noqa: T201
            
            # 1. Seed Provinces
            print("\n🌆 Seeding provinces...")  # noqa: T201
            provinces_created = 0
            
            for code, full_name in provinces_dict.items():
                # Check if province already exists
                result = await session.execute(
                    select(Province).where(Province.code == code)
                )
                existing_province = result.scalar_one_or_none()
                
                if existing_province:
                    print(f"   Province '{full_name}' already exists, skipping...")  # noqa: T201
                    continue
                
                province = Province(code=code, full_name=full_name)
                session.add(province)
                provinces_created += 1
                print(f"   ✓ Created province: {full_name}")  # noqa: T201
            
            await session.flush()
            print(f"✅ Provinces: {provinces_created}/{len(provinces_dict)} created")  # noqa: T201
            
            # 2. Seed Wards
            print("\n🏘️  Seeding wards...")  # noqa: T201
            wards_created = 0
            wards_skipped = 0
            
            for ward_data in wards_data:
                # Check if ward already exists
                result = await session.execute(
                    select(Ward).where(Ward.code == ward_data["code"])
                )
                existing_ward = result.scalar_one_or_none()
                
                if existing_ward:
                    wards_skipped += 1
                    if wards_skipped <= 10:  # Only show first 10 to avoid spam
                        print(f"   Ward '{ward_data['full_name']}' already exists, skipping...")  # noqa: T201
                    continue
                
                ward = Ward(**ward_data)
                session.add(ward)
                wards_created += 1
                
                # Print progress every 100 wards
                if wards_created % 100 == 0:
                    print(f"   Progress: {wards_created} wards created...")  # noqa: T201
            
            await session.commit()
            
            print(f"\n✅ Seed completed successfully!")  # noqa: T201
            print(f"   - Provinces: {provinces_created} created, {len(provinces_dict) - provinces_created} already existed")  # noqa: T201
            print(f"   - Wards: {wards_created} created, {wards_skipped} already existed")  # noqa: T201
            print(f"   - Total: {len(provinces_dict)} provinces, {len(wards_data)} wards in database")  # noqa: T201

        except Exception as e:
            await session.rollback()
            print(f"\n❌ Error seeding data: {e}")  # noqa: T201
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_locations())
