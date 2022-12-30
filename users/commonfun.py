
months = {
    '01':'Jan',
    '02':'Feb',
    '03':'Mar',
    '04':'Apr',
    '05':'May',
    '06':'Jun',
    '07':'Jul',
    '08':'Aug',
    '09':'Sep',
    '10':'Oct',
    '11':'Nov',
    '12':'Dec',
}

def CalculateDateTime(time):
    """
    Function for providing date and time in more readable form.
    """
    date=time.split('T')[0]
    time = time.split('T')[1]
    splitted_date = date.split('-')
    year = splitted_date[0]
    month = months[splitted_date[1]]
    day = splitted_date[2]
    hour = time.split(':')[0]
    minute = time.split(':')[1]
    fulldate = day+" "+month+" "+year+" | "+hour+":"+minute
    return fulldate