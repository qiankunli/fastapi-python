from enum import Enum
from typing import (
    Any,
    Generic,
    Iterable,
    Literal,
    Protocol,
    Sequence,
    Type,
    TypeVar,
    cast,
)

from pydantic import BaseModel
from sqlalchemy import (
    ColumnElement,
    Row,
    RowMapping,
    and_,
    asc,
    delete as sa_delete,
    desc,
    or_,
    select,
    update as sa_update,
)
from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.orm import Mapped, Session

from app.do.base import DOAttributeBase
from common.exception import errors
from common.log import log
from libs.database.session import get_session
from pkg.crud_plus.error import ModelColumnError, SelectExpressionError


class ExpressionLiteral(str, Enum):
    and_ = 'and'
    or_ = 'or'


# 定义一个协议，确保所有的模型都有一个 'id' 属性
class HasId(Protocol):
    # 可能是int 也可能是str
    id: Mapped[Any]


_Model = TypeVar('_Model', bound=HasId)
_CreateSchema = TypeVar('_CreateSchema', bound=BaseModel)
_UpsertSchema = TypeVar('_UpsertSchema', bound=BaseModel)
_UpdateSchema = TypeVar('_UpdateSchema', bound=BaseModel)


class CRUDPlus(Generic[_Model]):
    def __init__(self, model: Type[_Model]):
        self.model = model

    def do_to_model(self, obj, **kwargs):
        if isinstance(obj, self.model):
            return obj
        if isinstance(obj, DOAttributeBase):
            return obj.do_to_model(**kwargs)
        return self.model(**obj.model_dump(), **kwargs)

    def create_model(self, obj: _CreateSchema | _Model, **kwargs) -> None:
        """
        Create a new instance of a model

        :param session:
        :param obj:
        :param kwargs:
        :return:
        """
        session: Session = get_session()
        instance = self.do_to_model(obj, **kwargs)
        session.add(instance)
        session.flush()

    def create_models(self, objs: Iterable[_CreateSchema | _Model]) -> None:
        """
        Create new instances of a model

        :param session:
        :param obj:
        :return:
        """
        session: Session = get_session()
        instance_list = [self.do_to_model(i) for i in objs]
        session.add_all(instance_list)
        session.flush()

    def upsert_model(self, obj: _UpsertSchema | _Model, **kwargs) -> None:
        """
        upsert a new instance of a model
        :param session:
        :param obj:
        :param kwargs:
        :return:
        """
        session: Session = get_session()
        instance = self.do_to_model(obj, **kwargs)
        """执行 UPSERT 操作"""
        session.merge(instance)
        session.flush()

    def select_model_by_id(self, pk: str) -> _Model | None:
        """
        Query by ID

        :param session:
        :param pk:
        :return:
        """
        session: Session = get_session()
        query = session.execute(
            select(self.model).where(
                cast("ColumnElement[bool]", self.model.id == pk)
            )
        )
        return query.scalars().first()

    def select_model_by_column(self, column: str, column_value: Any) -> _Model | None:
        """
        Query by column

        :param session:
        :param column:
        :param column_value:
        :return:
        """
        session: Session = get_session()
        if hasattr(self.model, column):
            model_column = getattr(self.model, column)
            query = session.execute(select(self.model).where(model_column == column_value))  # type: ignore
            return query.scalars().first()
        else:
            raise ModelColumnError(f'Model column {column} is not found')

    def select_one_model_by_column(self, column: str, column_value: Any) -> _Model:
        """
        Select a unique model instance by column.

        :param column: The column to filter by.
        :param column_value: The value to filter the column by.
        :return: A unique model instance.
        :raises NoResultFound: If no result is found.
        :raises MultipleResultsFound: If multiple results are found.
        """
        session: Session = get_session()
        if hasattr(self.model, column):
            model_column = getattr(self.model, column)
            query = session.execute(select(self.model).where(model_column == column_value))  # type: ignore
            try:
                return query.scalars().one()
            except NoResultFound:
                raise NoResultFound(f'No result found for {column} = {column_value}')
            except MultipleResultsFound:
                raise MultipleResultsFound(f'Multiple results found for {column} = {column_value}')
        else:
            raise ModelColumnError(f'Model column {column} is not found')

    def select_model_by_columns(
            self, expression: ExpressionLiteral = ExpressionLiteral.and_, **conditions
    ) -> _Model | None:
        """
        Query by columns

        :param session:
        :param expression:
        :param conditions: Query conditions, format：column1=value1, column2=value2
        :return:
        """
        session: Session = get_session()
        where_list = self._get_where_conditions(conditions)
        match expression:
            case ExpressionLiteral.and_:
                query = session.execute(select(self.model).where(and_(*where_list)))
            case ExpressionLiteral.or_:
                query = session.execute(select(self.model).where(or_(*where_list)))
            case _:
                raise SelectExpressionError(f'select expression {expression} is not supported')
        return query.scalars().first()

    def _build_entity_query_by_columns(
            self, columns: list[str], expression: ExpressionLiteral = ExpressionLiteral.and_,
            **conditions):
        if len(columns) == 0:
            raise errors.NotFoundError(msg='no entities found in the query')
        if 'id' not in columns:
            columns.append('id')
        entities = [getattr(self.model, e) for e in columns]
        session: Session = get_session()
        where_list = self._get_where_conditions(conditions)
        match expression:
            case ExpressionLiteral.and_:
                query = session.execute(select(*entities).where(and_(*where_list)))
            case ExpressionLiteral.or_:
                query = session.execute(select(*entities).where(or_(*where_list)))
            case _:
                raise SelectExpressionError(f'select expression {expression} is not supported')
        return query

    def select_entities_by_columns(
            self, columns: list[str], expression: ExpressionLiteral = ExpressionLiteral.and_, **conditions
    ) -> Sequence[Row[tuple[Any]]]:
        """
        Query entities by columns

        :param session:
        :param expression:
        :param conditions: Query conditions, format：column1=value1, column2=value2
        :return:
        """
        query = self._build_entity_query_by_columns(columns, expression, **conditions)
        return query.fetchall()

    def select_entity_by_columns(
            self, columns: list[str], expression: ExpressionLiteral = ExpressionLiteral.and_, **conditions
    ) -> Row[Any] | None:
        """
        Query entity by columns

        :param session:
        :param expression:
        :param conditions: Query conditions, format：column1=value1, column2=value2
        :return:
        """
        query = self._build_entity_query_by_columns(columns, expression, **conditions)
        return query.first()

    def _get_where_conditions(self, conditions):
        where_list = []
        for column, value in conditions.items():
            if hasattr(self.model, column):
                model_column = getattr(self.model, column)
                where_list.append(model_column == value)
            else:
                raise ModelColumnError(f'Model column {column} is not found')
        return where_list

    def select_models(self) -> Sequence[Row | RowMapping | Any] | None:
        """
        Query all rows

        :param session:
        :return:
        """
        session: Session = get_session()
        query = session.execute(select(self.model))
        return query.scalars().all()

    def select_models_by_column(self, column: str, column_value: Any) -> Sequence[_Model]:
        """
        Select Models by column

        :param session:
        :param column:
        :param column_value:
        :return:
        """
        session: Session = get_session()
        if hasattr(self.model, column):
            model_column = getattr(self.model, column)
            query = session.execute(select(self.model).where(model_column == column_value))  # type: ignore
            return query.scalars().all()
        else:
            raise ModelColumnError(f'Model column {column} is not found')

    def select_models_order(
            self,
            *columns,
            model_sort: Literal['default', 'asc', 'desc'] = 'default',
    ) -> Sequence[Row | RowMapping | Any] | None:
        """
        Query all rows asc or desc

        :param session:
        :param columns:
        :param model_sort:
        :return:
        """
        sort_list = []
        session: Session = get_session()
        for column in columns:
            if hasattr(self.model, column):
                model_column = getattr(self.model, column)
                sort_list.append(model_column)
            else:
                raise ModelColumnError(f'Model column {column} is not found')
        match model_sort:
            case 'default':
                query = session.execute(select(self.model).order_by(*sort_list))
            case 'asc':
                query = session.execute(select(self.model).order_by(asc(*sort_list)))
            case 'desc':
                query = session.execute(select(self.model).order_by(desc(*sort_list)))
            case _:
                raise SelectExpressionError(f'select sort expression {model_sort} is not supported')
        return query.scalars().all()

    def update_model(self, pk: str, obj: _UpdateSchema | dict[str, Any], **kwargs) -> int:
        """
        Update an instance of model's primary key

        :param session:
        :param pk:
        :param obj:
        :param kwargs:
        :return:
        """
        session: Session = get_session()
        if isinstance(obj, dict):
            instance_data = obj
        else:
            instance_data = obj.model_dump(exclude_unset=True)
        if kwargs:
            instance_data.update(kwargs)
        result = session.execute(
            sa_update(self.model).where(
                cast('ColumnElement[bool]', self.model.id == pk),
            ).values(**instance_data)
        )
        session.flush()
        log.info(f'update_model result.rowcount {result.rowcount}')
        return result.rowcount  # type: ignore

    def update_model_by_column(
            self, column: str, column_value: Any, obj: _UpdateSchema | dict[str, Any], **kwargs
    ) -> int:
        """
        Update an instance of model column

        :param session:
        :param column:
        :param column_value:
        :param obj:
        :param kwargs:
        :return:
        """
        session: Session = get_session()
        if isinstance(obj, dict):
            instance_data = obj
        else:
            instance_data = obj.model_dump(exclude_unset=True)
        if kwargs:
            instance_data.update(kwargs)
        if hasattr(self.model, column):
            model_column = getattr(self.model, column)
        else:
            raise ModelColumnError(f'Model column {column} is not found')
        result = session.execute(
            sa_update(self.model).where(
                cast('ColumnElement[bool]', model_column == column_value)
            ).values(**instance_data)
        )
        session.flush()
        log.info(f'update_model_by_column result.rowcount {result.rowcount}')
        return result.rowcount  # type: ignore

    def update_model_by_columns(
            self, obj: _UpdateSchema | dict[str, Any],
            expression: ExpressionLiteral = ExpressionLiteral.and_,
            **conditions,
    ):
        session: Session = get_session()
        where_list = self._get_where_conditions(conditions)
        if isinstance(obj, dict):
            instance_data = obj
        else:
            instance_data = obj.model_dump(exclude_unset=True)
        match expression:
            case ExpressionLiteral.and_:
                result = session.execute(
                    sa_update(self.model).where(
                        and_(*where_list)
                    ).values(**instance_data)
                )
            case ExpressionLiteral.or_:
                result = session.execute(
                    sa_update(self.model).where(
                        or_(*where_list)
                    ).values(**instance_data)
                )
            case _:
                raise SelectExpressionError(f'sa_delete expression {expression} is not supported')
        session.flush()
        log.info(f'update_model_by_columns result.rowcount {result.rowcount}')
        return result.rowcount  # type: ignore

    def delete_model(self, pk: str, **kwargs) -> int:
        """
        Delete an instance of a model

        :param session:
        :param pk:
        :param kwargs: for soft deletion only
        :return:
        """
        session: Session = get_session()
        if not kwargs:
            result = session.execute(
                sa_delete(self.model).where(
                    cast('ColumnElement[bool]', self.model.id == pk)
                )
            )
        else:
            result = session.execute(
                sa_update(self.model).where(
                    cast("ColumnElement[bool]", self.model.id == pk)
                ).values(**kwargs)
            )
        session.flush()
        log.info(f'delete_model result.rowcount {result.rowcount}')
        return result.rowcount  # type: ignore

    def delete_model_by_columns(
            self, expression: ExpressionLiteral = ExpressionLiteral.and_, **conditions
    ) -> int:
        """
        Delete by columns

        :param session:
        :param expression:
        :param conditions: Delete conditions, format：column1=value1, column2=value2
        :return:
        """
        session: Session = get_session()
        where_list = self._get_where_conditions(conditions)
        match expression:
            case ExpressionLiteral.and_:
                result = session.execute(
                    sa_delete(self.model).where(
                        and_(*where_list)
                    )
                )
            case ExpressionLiteral.or_:
                result = session.execute(
                    sa_delete(self.model).where(
                        or_(*where_list)
                    )
                )
            case _:
                raise SelectExpressionError(f'sa_delete expression {expression} is not supported')
        session.flush()
        log.info(f'delete_model_by_columns result.rowcount {result.rowcount}')
        return result.rowcount  # type: ignore
