from sqlmodel import Session, select
from .models import DFPorSeun, DFFinal

def get_all_df_por_seun(session: Session):
    statement = select(DFPorSeun)
    results = session.exec(statement).all()
    return results

def get_all_df_final(session: Session):
    statement = select(DFFinal)
    results = session.exec(statement).all()
    return results

def save_df_por_seun(session: Session, df_por_seun: DFPorSeun):
    try:
        session.add(df_por_seun)
        session.commit()
        session.refresh(df_por_seun)
        return df_por_seun
    except Exception as e:
        session.rollback()
        logging.error(f"Error saving DFPorSeun: {e}")
        raise

def save_df_final(session: Session, df_final: DFFinal):
    session.add(df_final)
    session.commit()
    session.refresh(df_final)
    return df_final