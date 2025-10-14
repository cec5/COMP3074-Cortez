# Run the cosine similarity (either your own implementation or one of the two shown
# above) on the following set of test documents, with respect to a query q = [1, 2, 0, 0, 0, 0]:
# d1 = [6, 12, 0, 0, 0, 0]
# d2 = [2, 4, 0, 0, 0, 0]
# d3 = [3, 6, 0, 0, 0, 0]
# d4 = [0, 0, 1, 1, 0, 0]
# Note down sim(q, d1), sim(q, d2), sim(q, d3), and sim(q, d4). What do you observe and
# how do you explain it?

import scipy
from scipy import spatial

q = [1,2,0,0,0,0]
d1 = [6,12,0,0,0,0]
d2 = [2,4,0,0,0,0]
d3 =[3,6,0,0,0,0]
d4 = [0,0,1,1,0,0]

print("Query:",q)
print("\nTest Documents:\n"+str(d1)+"\n"+str(d2)+"\n"+str(d3)+"\n"+str(d4))
test = input("\nEnter the number of the test document to compare to the query: ")

if test == "1":
    print("Similarity: ",1-spatial.distance.cosine(q,d1))
elif test == "2":
    print("Similarity: ",1-spatial.distance.cosine(q,d2))
elif test == "3":
    print("Similarity: ",1-spatial.distance.cosine(q,d3))
elif test == "4":
    print("Similarity: ",1-spatial.distance.cosine(q,d4))
else:
    print("Incorrect input")
