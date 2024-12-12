#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from app.model.resource_model import ResourceModel
from pkg.crud_plus.crud import CRUDPlus


class CRUDResource(CRUDPlus[ResourceModel]):
    pass


resource_dao: CRUDResource = CRUDResource(ResourceModel)
