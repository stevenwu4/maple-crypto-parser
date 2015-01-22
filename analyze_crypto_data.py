"""
1. Split on *'s in between brackets
2. For each polynomial, sort contents in decreasing order of degree
3. Group all polynomials sorted in descending order by highest degree
4. Find number count of polynomials per degree

Usage:
    analyze_crypto_data.py (--filename=<filename>)
"""

from docopt import docopt
import re

POLYNOMIAL_REGEX = re.compile('\^([0-9]+)')
N_REGEX = re.compile('([0-9\^\*()]+)')


def sort_polynomial(polynomial):
    x_degree_map = {}
    constants = []
    terms = polynomial.split('+')
    
    #Split the terms of the polynomial into variables or constants
    for t in terms:
        #print 't: {0}'.format(t)
        match = re.search(POLYNOMIAL_REGEX, t)
        if match:
            degree = match.group(1)
            x_degree_map[degree] = t
        elif t.strip() == 'x':
            x_degree_map['1'] = t
        else:
            constants.append(t)
    #Assert that all the terms were accounted for
    assert(len(terms) == len(x_degree_map.keys())+len(constants))
    #Convert the list of strings into a list of ints
    list_of_degrees_as_ints = map(int, x_degree_map.keys())
    #Sort the degrees of the found variables by highest degree
    list_of_degrees_as_ints.sort()
    list_of_degrees_as_ints.reverse()
    #Build the polynomial in order of highest degree
    variables = []
    for d in list_of_degrees_as_ints:
        degree_key = str(d)
        variables.append(x_degree_map[degree_key])
    
    new_terms = variables + constants
    sorted_polynomial = '+'.join(new_terms)

    return sorted_polynomial


def get_highest_degree(sorted_polynomial):
    """
    Assumes that the input polynomial is sorted by sort_polynomial
    """
    terms = sorted_polynomial.split('+')
    highest_term = terms[0]

    match = re.search(POLYNOMIAL_REGEX, highest_term)
    if match:
        degree = match.group(1)
        return degree
    elif highest_term.strip() == 'x':
        return '1'
    else:
        return '0'


def build_polynomial_strings(deg_poly_map):
    clean_deg_poly_map = {}
    for deg, poly in deg_poly_map.iteritems():
        #Remove last comma at the end
        poly = poly[:len(poly)-1]
        new_poly = poly.replace(',', ')*(')
        new_str = '(' + new_poly + ')'
        clean_deg_poly_map[deg] = new_str
    return clean_deg_poly_map


if __name__ == '__main__':
    args = docopt(__doc__)
    filename = args['--filename']
    opened_data = open(filename, 'r')
    results_filename = filename + '_results'
    opened_results = open(results_filename, 'w')

    degree_count_map = {}
    degree_polynomial_map = {}
    n = ''
    for i, line in enumerate(opened_data):
        if 'n :=' in line:
            match = re.search(N_REGEX, line)
            if match:
                n = match.group()
                degree_count_map = {}
                degree_polynomial_map = {}
                opened_results.write('n = {0}\n'.format(n))
            else:
                raise Exception("This shouldn't happen!")
        if 'x' not in line or 'mod' in line or 'factor' in line:
            continue
        #print 'Line {0}: {1}'.format(i, line)
        polynomials = line.split(')*(')

        polynomials[0] = polynomials[0].replace('(', '')
        polynomials[len(polynomials) - 1] =\
        polynomials[len(polynomials) - 1].replace(')', '')

        for i, polynomial in enumerate(polynomials):
            sorted_p = sort_polynomial(polynomial)
            highest_degree = get_highest_degree(sorted_p)
            #Store counts for the highest degree seen
            count = degree_count_map.get(highest_degree, 0)+1
            degree_count_map[highest_degree] = count
            #Store the polynomial associated with the highest degree
            polynomial_str = degree_polynomial_map.get(
                highest_degree, ''
            )+sorted_p+','
            degree_polynomial_map[highest_degree] = polynomial_str

        #Sort the degrees of the found variables by degree
        degrees_as_ints = map(int, degree_count_map.keys())
        degrees_as_ints.sort()
        #Build the polynomial string to write to file
        clean_deg_poly_map = build_polynomial_strings(degree_polynomial_map)

        total_count = 0
        for d in degrees_as_ints:
            degree = str(d)
            count = degree_count_map[degree]
            poly_str = clean_deg_poly_map[degree]
            opened_results.write(
                'degree {0}: {1}: {2}\n'.format(degree, count, poly_str)
            )
            total_count += d
        if not total_count%2:
            print 'Total count not even number for {0}'.format(n)
        opened_results.write('\n\n')
