def parse(roll):
	branch_dict = {
	    '00' : 'CE',
	    '10' : 'CSE',
	    '13' : 'IT',
	    '30' : 'EE',
	    '43' : 'ME'
	}
	year = '20' + roll[0:2]
	t = roll[5:7]
	branch = branch_dict[t]
	return year, branch
