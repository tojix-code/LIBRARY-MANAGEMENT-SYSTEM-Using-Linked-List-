from graphviz import Digraph

# Create a new directed graph
dot = Digraph()

# Define nodes
dot.node('A', 'Start')
dot.node('B', 'Initialize LibraryApp')
dot.node('C', 'Display Main Menu')
dot.node('D', 'Add Book')
dot.node('E', 'Open Add Book Dialog')
dot.node('F', 'Input: Title, Author, ISBN')
dot.node('G', 'Validate Input')
dot.node('H', 'Call library.add_book(title, author, isbn)')
dot.node('I', 'Show Success/Error Message')
dot.node('J', 'Delete Book')
dot.node('K', 'Prompt for ISBN')
dot.node('L', 'Call library.delete_book(isbn)')
dot.node('M', 'Show Success/Error Message')
dot.node('N', 'View Books')
dot.node('O', 'Call library.view_books()')
dot.node('P', 'Generate HTML')
dot.node('Q', 'Open HTML in Browser')
dot.node('R', 'Upload PDF')
dot.node('S', 'Prompt for ISBN')
dot.node('T', 'Call library.upload_pdf(isbn)')
dot.node('U', 'Show Success/Error Message')
dot.node('V', 'View PDF')
dot.node('W', 'Prompt for ISBN')
dot.node('X', 'Call library.view_pdf(isbn)')
dot.node('Y', 'Show Success/Error Message')
dot.node('Z', 'Update Book')
dot.node('AA', 'Prompt for ISBN')
dot.node('AB', 'Check if book exists')
dot.node('AC', 'Open Update Book Dialog')
dot.node('AD', 'Input: New Title, New Author, New ISBN')
dot.node('AE', 'Validate Input')
dot.node('AF', 'Call library.update_book(isbn, title, author, new_isbn)')
dot.node('AG', 'Show Success/Error Message')
dot.node('AH', 'Undo Last Operation')
dot.node('AI', 'Call library.undo()')
dot.node('AJ', 'Show Success/Error Message')
dot.node('AK', 'Exit')
dot.node('AL', 'End')

# Define edges
dot.edges(['AB', 'BC', 'CD'])

dot.edge('C','D', label='Add Book')
dot.edge('C', 'J', label='Delete Book')
dot.edge('C', 'N', label='View Books')
dot.edge('C', 'R', label='Upload PDF')
dot.edge('C', 'V', label='View PDF')
dot.edge('C', 'Z', label='Update Book')
dot.edge('C', 'AH', label='Undo Last Operation')
dot.edge('C', 'AK', label='Exit')

# Add edges for Add Book process
dot.edge('D', 'E')
dot.edge('E', 'F')
dot.edge('F', 'G')
dot.edge('G', 'H')
dot.edge('H', 'I')

# Add edges for Delete Book process
dot.edge('J', 'K')
dot.edge('K', 'L')
dot.edge('L', 'M')

# Add edges for View Books process
dot.edge('N', 'O')
dot.edge('O', 'P')
dot.edge('P', 'Q')

# Add edges for Upload PDF process
dot.edge('R', 'S')
dot.edge('S', 'T')
dot.edge('T', 'U')

# Add edges for View PDF process
dot.edge('V', 'W')
dot.edge('W', 'X')
dot.edge('X', 'Y')

# Add edges for Update Book process
dot.edge('Z', 'AA')
dot.edge('AA', 'AB')
dot.edge('AB', 'AC')
dot.edge('AC', 'AD')
dot.edge('AD', 'AE')
dot.edge('AE', 'AF')
dot.edge('AF', 'AG')

# Add edges for Undo operation
dot.edge('AH', 'AI')
dot.edge('AI', 'AJ')

# Add edges for Exit
dot.edge('AK', 'AL')

# Set the DPI for better quality
dot.attr(dpi='600')  # You can set this to 300 or higher
dot.render('library_management_flowchart', format='png', cleanup=True)

print("Flowchart generated and saved as 'library_management_flowchart.png'")