

def generate():
	# generates three files of different sizes to test
	data = open("generated_points_100.txt", 'w')
	data.write("x, y, z, r, g, b\n")
	for x in range(-5, 6):
		for y in range(-5, 6):
			z = abs(x+y) - abs(y-x)
			data.write(str(x) + ", " + str(y) + ", " + str(z) + ", " + 
				str(abs(x + y + z) / 10.0) + ", " + 
				str(abs(x + y + z) / 10.0) + ", " + 
				str(abs(z / 10.0))+"\n")
	data.close()

	data = open("generated_points_500.txt", 'w')
	data.write("x, y, z, r, g, b\n")
	for x in range(-10, 11):
		for y in range(-10, 11):
			z = abs(x+y) - abs(y-x)
			data.write(str(x) + ", " + str(y) + ", " + str(z) + ", " + 
				str(abs(x / 10.0)) + ", " + 
				str(abs(x - y) / 10.0) + ", " + 
				str(abs(x - y + z) / 10.0)+"\n")
	data.close()

	data = open("generated_points_50000.txt", 'w')
	data.write("x, y, z, r, g, b\n")
	for x in range(-100, 101):
		for y in range(-100, 101):
			z = abs(x+y) - abs(y-x)
			data.write(str(x) + ", " + str(y) + ", " + str(z) + ", " + 
				str(abs(x / 10.0)) + ", " + 
				str(abs(y / 10.0)) + ", " + 
				str(abs(z / 10.0))+"\n")
	data.close()
if __name__ == "__main__":
	generate()