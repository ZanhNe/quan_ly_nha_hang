from contextlib import contextmanager
from sqlalchemy.exc import SQLAlchemyError
from app.extentions.extentions import db
from jwt import InvalidTokenError, ExpiredSignatureError


class TransactionManager:
    
    @contextmanager
    def transaction(self, error_message: str):
        # session = self.session()
        session = db.session()
        transaction_active = session.in_transaction()

        print(f'Bắt đầu khối "with", transaction_active: {transaction_active}')

        if not transaction_active:
            session.begin()
        try:
            yield session
            if not transaction_active:
                print('Nghiệp vụ thành công, transaction ngoài cùng đã commit')
                session.commit()
        except (SQLAlchemyError, InvalidTokenError, ExpiredSignatureError, Exception) as e:
            print(f'Lỗi xảy ra: {e}')   
            if not transaction_active:
                print('Transaction thất bại, đang rollback...')
                session.rollback()
            if isinstance(e, Exception):
                raise e
            elif isinstance(e, SQLAlchemyError):
                raise Exception(error_message)
            elif isinstance(e, InvalidTokenError):
                raise e
            elif isinstance(e, ExpiredSignatureError):
                raise e
            

transaction_manager = TransactionManager()


        
        