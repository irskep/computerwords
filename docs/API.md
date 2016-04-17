# API

<!-- break out plugin into module- and class-level as a test -->

<autodoc-python
    module="computerwords.plugin"
    include-children=False
    heading-level=2
    />

<autodoc-python
    class="computerwords.plugin.CWPlugin"
    include-children=True
    render-absolute-path=False
    heading-level=3 />

<!-- for everything else, use include-children=true -->

<autodoc-python
    module="computerwords.library"
    include-children=True
    heading-level=2
    />

<heading-alias name="cwtree" />

<autodoc-python
    module="computerwords.cwdom.CWTree"
    include-children=True
    heading-level=2
    />

<autodoc-python
    module="computerwords.cwdom.traversal"
    include-children=True
    heading-level=2
    />

<autodoc-python
    module="computerwords.cwdom.nodes"
    include-children=True
    heading-level=2
    />
