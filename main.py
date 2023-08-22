import streamlit as st
import pandas as pd
# import bar_chart_race as bcr
import bar_chart_race_cn as bcr
import streamlit.components.v1 as components
import base64


def dataFilter(data):
    # 设置界面UI
    container = st.container()
    container.markdown('## Data Filter')
    column2, column3 = container.columns(2)
    button1 = column2.button('Add Conditions')
    button2 = column3.button('Remove Conditions')
    # 初始条件数目为0
    condition_num = st.session_state.get('condition_num', 0)

    if button1:
        condition_num += 1
        st.session_state['condition_num'] = condition_num

    if button2 and condition_num > 0:
        condition_num -= 1
        st.session_state['condition_num'] = condition_num
    #  在表格中添加筛选条件
    container_form = container.form(key='container_form')
    conditions = []
    logical_oper_list = []
    if condition_num > 0:
        for i in range(condition_num):
            if i == 1:
                input_column1, input_operator, input_value = container_form.columns(3)
                column1 = input_column1.selectbox(label='Select Column', key='input_column' + str(i),
                                                  options=list(data.columns))
                operator = input_operator.selectbox(label='Select Operator', key='operator' + str(i),
                                                    options=['>', '<', '==', '!=', 'contains', '>=', '<='])
                value = input_value.text_input(label='Enter Value', key='value' + str(i))
                # 如果该column的类型为float或者int，则将value转换为float或者int
                # 对于数值型的数据，将输入的value转换为float或者int
                if value:
                    if data.dtypes[column1] == 'float64' or data.dtypes[column1] == 'int64':
                        value = float(value)
                conditions.append({'column': column1, 'operator': operator, 'value': value})
                # conditions.append({'column': column1, 'operator': operator, 'value': value})
            elif i > 1:
                # 当筛选条件数目大于1时，需要选择逻辑运算符
                logical_cloumn, input_column1, input_operator, input_value = container_form.columns(4)
                logical_operator = logical_cloumn.selectbox(label='Select Logical Operator', key='logical' + str(i),
                                                            options=['and', 'or'])
                column1 = input_column1.selectbox(label='Select Column', key='input_column' + str(i),
                                                  options=list(data.columns))
                operator = input_operator.selectbox(label='Select Operator', key='operator' + str(i),
                                                    options=['>', '<', '==', '!=', 'contains', '>=', '<='])
                value = input_value.text_input(label='Enter Value', key='value' + str(i))
                # 如果该column的类型为float或者int，则将value转换为float或者int
                # 对于数值型的数据，将输入的value转换为float或者int
                if value:
                    if data.dtypes[column1] == 'float64' or data.dtypes[column1] == 'int64':
                        value = float(value)
                conditions.append({'column': column1, 'operator': operator, 'value': value})
                logical_oper_list.append({'logical_operator': logical_operator})
    submit_button = container_form.form_submit_button(label='OK')
    if submit_button:
        if len(conditions) > 0:
            data = dataFilterFunction(data, conditions, logical_oper_list)
        st.session_state['condition_num'] = 0
        st.session_state['data'] = data


def dataFilterFunction(data, conditions, logical_oper_list):
    # 根据conditions 和 logical_oper_list中的条件对data进行筛选
    operators = {  # 定义各种运算符对应的操作
        'contains': lambda column, value: data[column].str.contains(value),
        '>': lambda column, value: data[column] > value,
        '<': lambda column, value: data[column] < value,
        '==': lambda column, value: data[column] == value,
        '!=': lambda column, value: data[column] != value,
        '>=': lambda column, value: data[column] >= value,
        '<=': lambda column, value: data[column] <= value
    }
    bool_condition = []
    for condition in conditions:
        operator = condition['operator']
        column = condition['column']
        value = condition['value']
        if operator in operators:
            bool_condition.append(operators[operator](column, value))
    # 将所有的条件用logical_oper_list中的逻辑运算符连接起来
    final_condition = bool_condition[0]
    for i in range(len(logical_oper_list)):
        if logical_oper_list[i]['logical_operator'] == 'and':
            final_condition = final_condition & bool_condition[i + 1]
        elif logical_oper_list[i]['logical_operator'] == 'or':
            final_condition = final_condition | bool_condition[i + 1]
    return data[final_condition]


def bcrPainter():
    st.markdown('## BCR Setting')
    data = st.session_state.get('data', None)
    if data is None:
        return
    columns = list(data.columns)
    # Creating Dropdown
    if columns is not None:
        setting_form = st.form(key='setting_form')

        title = setting_form.text_input(label='Enter Title')
        value_column, perido_column, category_column = setting_form.columns(3)
        value_name = value_column.selectbox('Select Data: ', columns)
        period = perido_column.selectbox('Select Period: ', columns)
        category = category_column.selectbox('Select Category: ', columns)
        # detail_setting = setting_form.multiselect('Detail Setting', columns)
        # Defining submit button

        submit_button = setting_form.form_submit_button(label='Generate BCR')
        show_sidebar = st.sidebar.checkbox("Detail Setting of BCR", value=True, )

        if  show_sidebar:
            max_bar_size = st.sidebar.number_input("Max Number of Bars ", value=5)
            orientation = st.sidebar.selectbox("Orientation", ["h", "v"])
            sort = st.sidebar.selectbox("Sort", ["asc", "desc"])
            steps_per_period = st.sidebar.number_input("Steps Per Period", value=5)
            period_length = st.sidebar.number_input("Period Length（ms）", value=100)
            fixed_max = st.sidebar.checkbox("Fixed Max", value=True)
            bar_size = st.sidebar.number_input("Bar Size", value=0.95)

            # if st.button("Generate BCR"):
            if submit_button:
                with st.spinner('Generating BCR...'):
                    drawBCR(value_name, period, category, title, max_bar_size, orientation, sort, steps_per_period,
                            period_length, fixed_max, bar_size)
        # if submit_button:
        #     with st.sidebar:
        #         max_bar_size = st.sidebar.number_input("Max Number of Bars ", value=5)
        #         # h条形图 v柱状图
        #         orientation = st.selectbox("Orientation", ["h", "v"])
        #         # 降序，asc-升序
        #         sort = st.selectbox("Sort", ["Descending", "Ascending"])
        #         # 图像帧数。数值越小，越不流畅。越大，越流畅。
        #         steps_per_period = st.number_input("Steps Per Period", value=5)
        #         # 设置帧率，单位时间默认为500ms。每个period的总时间是500ms
        #         period_length = st.number_input("Period Length（ms）", value=100)
        #         # 固定数值轴，使其不发生动态变化 true-固定
        #         fixed_max = st.checkbox("Fixed Max", value=True)
        #         # 条形图高度
        #         bar_size = st.number_input("Bar Size", value=0.95)
        #         # 添加一个提交按钮
        #         if st.button("Generate BCR"):
        #             # 调用函数，并传递设置的参数
        #             with st.spinner('Generating BCR...'):
        #                 drawBCR(value_name, period, category, title, max_bar_size, orientation, sort, steps_per_period,
        #                         period_length, fixed_max, bar_size)
        #                 # drawBCR(value_name, period, category, title, 5)
        #     columns = None


    else:
        st.write('No Valid Columns')


def drawBCR(value_name, period, category, title, max_bar_size=5, orientation='h', sort='desc', steps_per_period=10,
            period_length=200, fixed_max=True, bar_size=0.95):
    df_values, df_ranks = bcr.prepare_long_data(df=st.session_state['data'], index=period, columns=category,
                                                values=value_name)
    html_sr = bcr.bar_chart_race(df_values, title=title,sort=sort, steps_per_period=steps_per_period,orientation=orientation,n_bars=max_bar_size,
                                    period_length=period_length, fixed_max=fixed_max, bar_size=bar_size,bar_kwargs={'alpha': .2, 'ec': 'black', 'lw': 3}).data
    # components.html(html_sr)

    start = html_sr.find('base64,') + len('base64,')
    end = html_sr.find('">', start)
    video = base64.b64decode(html_sr[start:end])
    st.video(video)


# 基本界面
st.title("Generate Bar_Chart_Race")
data_file = st.file_uploader("Upload CSV", type=["csv"])
if data_file is not None:
    data = pd.read_csv(data_file)
    dataFilter(data)
    bcrPainter()



else:
    st.write("No CSV File is Uploaded")
