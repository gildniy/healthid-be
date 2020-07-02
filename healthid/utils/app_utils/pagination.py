from django.core.paginator import Paginator


def pagination_query(query_set, page_count, page_number):
    """
    Breaks down retrieved records into chunks per page
    :param query_set: Query Set to be paginated
    :param page_count: Number of records in each page.
    :param page_number: The actual page
    :returns a tuple of the paginated record,
    number of pages and the total number of items
    """
    paginator = Paginator(query_set, page_count)
    return paginator.get_page(page_number), paginator.num_pages, len(query_set)
