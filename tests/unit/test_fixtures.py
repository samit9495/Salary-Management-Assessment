from sqlalchemy import text
from sqlalchemy.orm import Session


def test_db_fixture_yields_a_clean_session(db: Session) -> None:
    assert db.execute(text("SELECT 1")).scalar() == 1
