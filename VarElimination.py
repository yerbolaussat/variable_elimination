# CS 686
# Yerbol Aussat
#SID: 20698564

import numpy as np

# Restricting a factor
def restrict(factor, variable, value):
	slc = [slice(None)] * factor.ndim
	slc[variable] = value	
	return factor[slc]
		
# Product of two factors
def multiply(factor1, factor2, vars1, vars2, variables):
	
	#print variables
	#print vars1
	#print vars2

	productVars = []
	for v in variables:
		if v in vars1 or v in vars2:
			productVars.append(v)
	#print productVars
	
	newShape1 = []
	newShape2 = []
	
	for v in productVars:
		if v in vars1:
			newShape1 = newShape1 + [2]
		else:
			newShape1 = newShape1 + [1] 
			
		if v in vars2:
			newShape2 = newShape2 + [2]
		else:
			newShape2 = newShape2 + [1] 		

	h = factor1.reshape(newShape1) * factor2.reshape(newShape2)
	#h = h.squeeze()
	return h, productVars

# Summing a variable out of a factor
def sumout(factor, variable):
	return factor.sum(axis = variable)	
	
# Normalization of a factor
def normalize(factor):
	return factor / factor.sum()

# given a list of all variables, query variable and evidence list
# returns a list of hidden variables
def get_hidden_variables(queryVariables, var_order, evidence_list):
	vars = list(var_order)
	
	for v in var_order:
		if v in evidence_list:
			indexE = vars.index(v)
			del vars[indexE]
	indexQ = vars.index(queryVariables)
	del vars[indexQ]
	var_order = vars
	return var_order

# returns dimension number of a variable in a factor
def getVarDimension(vars_of_factor, var):
	return vars_of_factor.index(var)
	

# variable elimination algorithm
def inference(factor_list, queryVariables, var_order, evidence_list, factorVars, variables):
	
	# hidden variables in order of summing out
	var_order = get_hidden_variables(queryVariables, var_order, evidence_list)
		
	factor_list_temp = factor_list.copy()
	factorVars_temp = factorVars.copy()
	
	# STEP 1: applying evidence to initial factors
	
	# printing all initial factors and their variables
	print "Initial factors:"
	print factorVars
	print factor_list
	
	for f in factor_list:
		for e in evidence_list:
			#print "\n\n\nfactorVar ", factorVars_temp[f]
			#print "f", f
			#print "evidence" , e
			
			if e in factorVars_temp[f]:				
				dim = getVarDimension(factorVars_temp[f], e)			
				g = restrict(factor_list_temp[f], dim, evidence_list[e])
				
				# adding a new reduced factor to factor_list and factorVars
				nextIndex = factor_list_temp.keys()[-1] + 1
				#print nextIndex
				factor_list_temp[nextIndex] = g
				del factorVars_temp[f][factorVars_temp[f].index(e)]
				factorVars_temp[nextIndex] = factorVars_temp[f]
				
				print "Applying evidences to initial factors:"
				print factorVars_temp[nextIndex]
				print factor_list_temp[nextIndex]
				
				# deleting old factors that were reduced from factor_list and factorVars
				del factor_list_temp[f]
				del factorVars_temp[f]
				f = nextIndex
	#updating factor_list and factorVars	
	factor_list = factor_list_temp
	factorVars = factorVars_temp
	
	# STEP 2: summing out hidden variables
	
	factor_list_temp = factor_list.copy()
	factorVars_temp = factorVars.copy()
	
	for hid_var in var_order:
		n = 0
		currentProductIndex = 0
		
		for f in factor_list:
			
			if hid_var in factorVars[f]:
				if n < 1:
					currentProductIndex = f
					n = n + 1
					
				else:
					# multiplying 2 factors
					productFactor = factor_list_temp[currentProductIndex]
					productVars = factorVars_temp[currentProductIndex]
					productFactor, productVars = multiply(productFactor, factor_list_temp[f], productVars, factorVars_temp[f], variables)

					# adding a new product factor to the end of factor_list and factorVars
					nextIndex = factor_list_temp.keys()[-1] + 1
					factor_list_temp[nextIndex] = productFactor
					factorVars_temp[nextIndex] = productVars
					#print factorVars_temp
					
					# deleting old factors that were used for multiplication
					del factor_list_temp[f]
					del factorVars_temp[f]
					del factor_list_temp[currentProductIndex]
					del factorVars_temp[currentProductIndex]
					currentProductIndex = nextIndex
		
		if n == 1:
			productFactor = factor_list_temp[currentProductIndex] 
			productVars = factorVars_temp[currentProductIndex]

		dim = getVarDimension(productVars, hid_var)			
		sumOverHidVar = sumout(productFactor, dim)
		
		# adding "sumout" factor to the factor list
		nextIndex = factor_list_temp.keys()[-1] + 1
		factor_list_temp[nextIndex] = sumOverHidVar
		del productVars[productVars.index(hid_var)]
		factorVars_temp[nextIndex] = productVars
		
		# printing new "summed out" factors:
		print "Summed out product: "
		print factorVars_temp[nextIndex]
		print factor_list_temp[nextIndex]
		
		# deleting old "used" factors
		del factor_list_temp[currentProductIndex]
		del factorVars_temp[currentProductIndex]
		factorVars = factorVars_temp.copy()
		factor_list = factor_list_temp.copy()
	
	#updating factorVars and factor_list
	factorVars = factorVars_temp.copy()
	factor_list = factor_list_temp.copy()
		
	# STEP 3: Product of factors with quiery variables
	#Normalization
		
	n = 0
	
	for f in factor_list:
		
		if len(factorVars[f]) == 0:
			del factor_list_temp[f]
			del factorVars_temp[f]
			continue
		if n < 1:
			currentProductIndex = f
			n = n + 1		
		else:
			productFactor = factor_list_temp[currentProductIndex]
			productVars = factorVars_temp[currentProductIndex]
			
			productFactor, productVars = multiply(productFactor, factor_list_temp[f], productVars, factorVars_temp[f], variables)
			
			# adding new factor to the factor list
			nextIndex = factor_list_temp.keys()[-1] + 1
			factor_list_temp[nextIndex] = productFactor
			factorVars_temp[nextIndex] = productVars
					
			# deleting old "used" factors that were used for multiplication
			del factor_list_temp[f]
			del factorVars_temp[f]
			del factor_list_temp[currentProductIndex]
			del factorVars_temp[currentProductIndex]
			currentProductIndex = nextIndex
	
	factor_list = factor_list_temp
	
	# factor with the query variable
	result = factor_list[currentProductIndex]

	answer = normalize(result)
	# final factor that contains probability distribution of query variable
	print "Product of factors with query variable; Normalization:"
	print productVars
	print answer
	return answer
	

def main():

	# REMARK: when creating new factors, make sure the dimensions are ordered
	# as specified in the variables Alphabet
	
	# f0(Tr)
	f0 = np.array([0.95, 0.05])	
		  
	# f1(FP, Fr, TR)	
	f1 = np.array(
					[[[0.99, 0.1],
				   	[0.9, 0.1]],
				   
				   [[0.01, 0.9],
				   [0.1, 0.9]]])   
				   
	# f2(Fr, TR)
	f2 = np.array([[0.996, 0.99],
				  [0.004, 0.01]])
				  
	# f3(IP, OC, Fr)	
	f3 = np.array(
					[[[0.999, 0.949],
				   	[0.9, 0.85]],
				   
				   [[0.001, 0.051],
				   [0.1, 0.15]]])
				   
	# f4(OC)			  
	f4 = np.array([0.2, 0.8])
				  
	# f5(CRP, OC)
	f5 = np.array([[0.99, 0.9],
				  [0.01, 0.1]])
				  
	# Order for relevant variable elimination
	varOrder = ["Tr", "FP", "Fr", "IP", "OC", "CRP"]
	
	# "Alphabetical" order for variables (useful for multiplication)
	variables = ["IP", "CRP", "OC", "FP", "Fr", "Tr"] 

	'''
	# PROBLEM 2B-1	
	
	#factors dictionary
	factors = {0:f0, 2:f2}
	#dictionary of variables for each factor
	factorVars = {0:["Tr"], 2:["Fr", "Tr"]}	
	
	# relevant variables ordered for summing out
	varOrder = ["Tr", "Fr"]

	#variables that each of the factors has
	factorVars = {0:["Tr"], 2:["Fr", "Tr"]}	
	
	evidence_list = {}
	quieryVar = "Fr"
		
	prob_distrib = inference(factors, quieryVar, varOrder, evidence_list, factorVars, variables)
	print "\nProblem 2B-1"
	print "Probability Distribution of ", quieryVar, " given ", evidence_list, " is ", prob_distrib, "\n\n\n"
	'''
	# PROBLEM 2B2	
	#factors dictionary
	factors = {0:f0, 1:f1, 2:f2, 3:f3, 4:f4, 5:f5}
	#dictionary of variables for each factor
	factorVars = {0:["Tr"], 1:["FP", "Fr", "Tr"], 2:["Fr", "Tr"], 3:["IP", "OC", "Fr"], 4:["OC"], 5:["CRP", "OC"]}	
	
	evidence_list = {"FP": 1, "IP" : 0, "CRP" : 1}
	quieryVar = "Fr"
		
	prob_distrib1 = inference(factors, quieryVar, varOrder, evidence_list, factorVars, variables)
	print "\nProblem 2B-2"
	print "Probability Distribution of ", quieryVar, " given ", evidence_list, " is ", prob_distrib1, "\n\n\n"
	
	'''
	# PROBLEM 2C	
	#factors dictionary
	factors = {0:f0, 1:f1, 2:f2, 3:f3, 4:f4, 5:f5}
	#dictionary of variables for each factor
	factorVars = {0:["Tr"], 1:["FP", "Fr", "Tr"], 2:["Fr", "Tr"], 3:["IP", "OC", "Fr"], 4:["OC"], 5:["CRP", "OC"]}	
	
	evidence_list = {"FP": 1, "IP" : 0, "CRP" : 1, "Tr" : 1}
	quieryVar = "Fr"
		
	prob_distrib1 = inference(factors, quieryVar, varOrder, evidence_list, factorVars, variables)
	print "\nProblem 2C"
	print "Probability Distribution of ", quieryVar, " given ", evidence_list, " is ", prob_distrib1, "\n\n\n"
	
	
	# PROBLEM 2D-1	
	#factors dictionary
	factors = {0:f0, 2:f2, 3:f3, 4:f4}
	#dictionary of variables for each factor
	factorVars = {0:["Tr"], 2:["Fr", "Tr"], 3:["IP", "OC", "Fr"], 4:["OC"]}	

	# relevant variables ordered for summing out
	varOrder = ["Tr", "Fr", "IP", "OC"]
	
	evidence_list = {"IP" : 1}
	quieryVar = "Fr"
		
	prob_distrib1 = inference(factors, quieryVar, varOrder, evidence_list, factorVars, variables)
	print "\nProblem 2D-1"
	print "Probability Distribution of ", quieryVar, " given ", evidence_list, " is ", prob_distrib1, "\n\n\n"
	
	
	# PROBLEM 2D-2	
	#factors dictionary
	factors = {0:f0, 1:f1, 2:f2, 3:f3, 4:f4}
	#dictionary of variables for each factor
	factorVars = {0:["Tr"], 1:["FP", "Fr", "Tr"], 2:["Fr", "Tr"], 3:["IP", "OC", "Fr"], 4:["OC"]}	
	
	# relevant variables ordered for summing out
	varOrder = ["Tr", "FP", "Fr", "IP", "OC"]
	
	evidence_list = {"IP" : 1, "FP" : 0}
	quieryVar = "Fr"
		
	prob_distrib1 = inference(factors, quieryVar, varOrder, evidence_list, factorVars, variables)
	print "\nProblem 2D-2"
	print "Probability Distribution (Domestic Purchase) of ", quieryVar, " given ", evidence_list, " is ", prob_distrib1, "\n\n\n"
	
	
	# PROBLEM 2D-3	
	#factors dictionary
	factors = {0:f0, 2:f2, 3:f3, 4:f4, 5:f5}
	factorVars = {0:["Tr"], 1:["FP", "Fr", "Tr"], 2:["Fr", "Tr"], 3:["IP", "OC", "Fr"], 4:["OC"]}	
	factorVars = {0:["Tr"], 2:["Fr", "Tr"], 3:["IP", "OC", "Fr"], 4:["OC"], 5:["CRP", "OC"]}	
	
	#relevant variables in the order of summing out
	varOrder = ["Tr", "Fr", "IP", "OC", "CRP"]
	
	evidence_list = {"IP" : 1, "CRP" : 1}
	quieryVar = "Fr"

	prob_distrib1 = inference(factors, quieryVar, varOrder, evidence_list, factorVars, variables)
	print "\nProblem 2D-3"
	print "Probability Distribution (Recent CRP) of ", quieryVar, " given ", evidence_list, " is ", prob_distrib1, "\n\n\n"
	'''
	
if __name__ == "__main__":
    main()

