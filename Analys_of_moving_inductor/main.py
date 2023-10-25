import pandas as pd
import numpy as np


'''Анализ перемещения 3-х подвесок индукторов на разных сортаментах труб. 
Вопрос: На каком типоразмере трубы больше всех перемещается подвеска?'''

# Отображение всех столбцов
desired_width = 500
pd.set_option('display.width', desired_width)
np.set_printoptions(linewidth=desired_width)
pd.set_option('display.max_columns', 10)

def calculation_of_time_for_moving_LTO(df):
    df['Time'] = 200
    df['Thickness'] = df['Thickness'] / 10
    df['Diametr'] = df['Diametr'] / 10
    df['speed_of_roll'] = df['speed_of_roll'].apply(lambda x: float(str(x).replace(',', '.')))
    # Расчет времени на производство трубы в часах
    time_of_produce_pipe_for_frame = \
        df[df['speed_of_roll'] > 100].groupby(['Thickness', 'Diametr'], as_index=False)['Time'].sum()
    time_of_produce_pipe_for_frame['Total_time'] = time_of_produce_pipe_for_frame['Time'] / 360000

    # Рассчет времени на перемещение головки (farward) и обьединение с общей таблицей диаметра и толщины стенки
    # Фильтрация по скорости стана больше 100 мм/мин
    time_of_move_forward_head = \
        df[(df['speed_of_roll'] > 100) & (df['signal_to_move_forward'] == 1.00)].groupby(
            ['Thickness', 'Diametr'], as_index=False)['Time'].sum()
    time_of_move_forward_head['Time_of_move_forward'] = time_of_move_forward_head['Time'] / 360000
    joined_table_for_frame = time_of_produce_pipe_for_frame.merge(time_of_move_forward_head,
                                                                      on=['Thickness', 'Diametr'], how='left')
    joined_table_for_frame['per_of_time_for_move_forward'] = (joined_table_for_frame['Time_of_move_forward'] /
                                                                joined_table_for_frame['Total_time']) * 100

    # Рассчет времени на перемещение головки (backward) и обьединение с общей таблицей диаметра и толщины стенки
    time_of_move_backward_head = \
        df[(df['speed_of_roll'] > 100) & (df['signal_to_move_backward'] == 1.00)].groupby(
            ['Thickness', 'Diametr'], as_index=False)['Time'].sum()
    time_of_move_backward_head['Time_of_move_backward'] = time_of_move_backward_head['Time'] / 360000
    joined_table_for_frame = joined_table_for_frame.merge(time_of_move_backward_head, on=['Thickness', 'Diametr'],
                                                              how='left')
    joined_table_for_frame['per_of_time_for_move_backward'] = (joined_table_for_frame['Time_of_move_backward'] /
                                                                 joined_table_for_frame['Total_time']) * 100
    joined_table_for_frame['Per_of_time_without_moving'] = 100 - joined_table_for_frame['per_of_time_for_move_backward'] - \
                                                  joined_table_for_frame['per_of_time_for_move_forward']
    end_table_for_frame = joined_table_for_frame.drop(['Time_x', 'Time_y', 'Time'], axis=1)
    end_table_for_frame = end_table_for_frame.drop(end_table_for_frame.index[[0]])
    return end_table_for_frame

df_1_frame = pd.read_csv('Data_1_frame.txt', sep=';', encoding='UTF-8')
df_2_frame = pd.read_csv('Data_2_frame.txt', sep=';', encoding='UTF-8')
df_3_frame = pd.read_csv('Data_3_frame.txt', sep=';', encoding='UTF-8')
frames = [df_1_frame,df_2_frame,df_3_frame]
for i in range(len(frames)):
    print('Frame LTO ' + str(i+1))
    print(calculation_of_time_for_moving_LTO(frames[i]))
