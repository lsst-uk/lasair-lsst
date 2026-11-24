from django.views.generic import RedirectView

from lasair.context_processors import global_vars


class DocsRedirectView(RedirectView):
    """*send an old website route to a page of the Lasair documentation*

    **Key Arguments:**

    - ``docsPage`` -- path of the page under the docs root, e.g. ``more_info/contact.html``

    **Usage:**

        path('contact', DocsRedirectView.as_view(docsPage='more_info/contact.html'))
    """
    permanent = False
    docsPage = None

    def get_redirect_url(self, *args, **kwargs):
        # THE DOCS ROOT FOLLOWS DEV_DOCS, THE SAME AS THE SIDEBAR LINKS
        return f"{global_vars(self.request)['docroot']}/{self.docsPage}"
