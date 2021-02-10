from PySide2.QtCore import Qt
from PySide2.QtSql import QSqlQuery, QSqlTableModel
from PySide2.QtWidgets import QItemDelegate, QDoubleSpinBox
from utils.util import Formula


class DontEditDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super(DontEditDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        return None


class FloatEditDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super(FloatEditDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        q = QDoubleSpinBox(option.widget)
        q.setDecimals(4)
        q.setRange(0, 10000000)
        q.setValue(float(index.data()))
        return q


class TableField(object):
    def __init__(self, field_name, column_name, delegate=None, default_value=None, help_text=None):
        self.column_name = column_name
        self.field_name = field_name
        self.delegate = delegate
        self.default_value = default_value
        self.help_text = help_text


class MyFundQSqlTableModel(QSqlTableModel):
    """自定义基金表格

    Args:
        QSqlTableModel ([type]): [description]
    """
    _id = TableField('id', 'Id', delegate=[DontEditDelegate])
    code = TableField('code', '基金代码', delegate=[
                      DontEditDelegate], default_value='')
    name = TableField('name', '基金名称', delegate=[
                      DontEditDelegate], default_value='')
    type_ = TableField('type', '基金类型', delegate=[
                       DontEditDelegate], default_value='')
    unit_value = TableField('unit_value', '最新净值', delegate=[
                            DontEditDelegate], default_value=0)
    assess_unit_value = TableField(
        'assess_unit_value', '预估净值', delegate=[DontEditDelegate], default_value=0)
    assess_growth_rate = TableField(
        'assess_growth_rate', '预估增长率', delegate=[DontEditDelegate], default_value=0)
    hold_cost = TableField('hold_cost', '持仓成本单价', delegate=[
                           FloatEditDelegate], default_value=0)
    hold_money = TableField('hold_money', '持仓总金额',
                            delegate=[FloatEditDelegate], default_value=0)
    hold_share = TableField('hold_share', '持仓份额', delegate=[
                            DontEditDelegate], default_value=0)
    assess_profit = TableField(
        'assess_profit', '预估收益', delegate=[DontEditDelegate], default_value=0)

    def __init__(self, parent=None, db=None):
        super(MyFundQSqlTableModel, self).__init__(parent, db)
        self.setTable('my_fund')
        self.setEditStrategy(self.OnFieldChange)
        for index, column in enumerate(self.columns()):
            self.setHeaderData(index, Qt.Horizontal, column.column_name)
            for _delegate in column.delegate:
                self.parent().setItemDelegateForColumn(index, _delegate(self))

        self.setQuery(QSqlQuery(
            'SELECT {} FROM my_fund'.format(
                ','.join(
                    [v.field_name for v in self.columns()]
                )
            )))
        self.select()

        self.beforeInsert.connect(self.befor_insert)

    def befor_insert(self, record):
        columns = self.columns()
        for column in columns:
            if record.isNull(column.field_name):
                record.setValue(column.field_name, column.default_value)

    def add_row(self, data):
        """添加一条记录

        Args:
            data ([type]): [description]

        Returns:
            [type]: [description]
        """
        record = self.record()
        for k, v in data.items():
            record.setValue(k, v)
        result = self.insertRecord(self.rowCount(), record)
        if result:
            self.select()
            return True
        return False

    def update_row(self, data):
        match = self.find_code_index(data.get('code'))
        if not match:
            return False

        record = self.find_by_code(data.get('code'))
        for k, v in data.items():
            record.setValue(k, v)

        # 更新持仓金额
        if record.value('hold_share') and record.value('unit_value'):
            record.setValue('hold_money', Formula.hold_money(
                record.value('unit_value'), record.value('hold_share')))

        # 更新预估收益
        if record.value('assess_unit_value') and data.get('prev_unit_value') and record.value('hold_share'):
            record.setValue('assess_profit', Formula.profit(record.value(
                'assess_unit_value'), data.get('prev_unit_value'), record.value('hold_share')))

        for column in self.columns():
            if record.value(column.field_name):
                self.setData(self.index(match.row(), self.fieldIndex(
                    column.field_name)), record.value(column.field_name))
        # self.submit()

    def find_code_index(self, fund_code):
        """查找基金代码

        Args:
            fund_code ([type]): [description]

        Returns:
            [type]: [description]
        """
        match = self.match(self.index(0, 1), Qt.DisplayRole, fund_code)
        if match:
            return match[0]
        return False

    def find_by_code(self, fund_code):
        q = QSqlQuery(
            "SELECT {} FROM my_fund WHERE `code`='{}'".format(','.join([v.field_name for v in self.columns()]), fund_code))
        q.first()
        if not q.record().value('code'):
            return False
        return q.record()

    def get_fund_code_all(self):
        """获取所有的基金代码

        Returns:
            [type]: [description]
        """
        codes = []
        for index in range(0, self.rowCount()):
            codes.append(self.record(index).value('code'))
        return codes

    def columns(self):
        keys = MyFundQSqlTableModel.__dict__.keys()

        columns = []
        for field in keys:
            if (isinstance(getattr(self, field), TableField)):
                columns.append(getattr(self, field))

        return columns
