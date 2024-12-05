import textwrap

def group_and_aggregate(df, group_var, count_var, out_varname):
    df = df.groupby(['member_party', group_var]).agg({count_var: 'sum'}).reset_index()
    df[out_varname] = df[count_var]*100 / df.groupby('member_party')[count_var].transform('sum')

    # wrap text for later
    df[group_var] = df[group_var].apply(lambda x: '<br>'.join(textwrap.wrap(x, 30)))
    return df

def filter_data_by_filters(data, table_name, selected_parliament, selected_constituency, selected_member):
    df = data[table_name]

    # Filter by parliament
    df = df[df['parliament'] == selected_parliament]
    
    # Further filter based on selected_constituency
    if selected_constituency != 'All':
        df = df[df['member_constituency'] == selected_constituency]
    
    # Further filter based on selected_member
    if selected_member != 'All':
        df = df[df['member_name'] == selected_member]

    return df

