<?xml version='1.0'?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:doc="http://nwalsh.com/xsl/documentation/1.0"
                xmlns:dyn="http://exslt.org/dynamic"
                xmlns:saxon="http://icl.com/saxon"
                exclude-result-prefixes="doc dyn saxon"
                version='1.0'>

<xsl:include href="param.xsl" />
<xsl:include href="../common/common.xsl" />
<xsl:include href="../lib/dumpfragment.xsl"/>
<xsl:include href="dtbl.xsl"/>
<xsl:include href="chunk-common.xsl" />
<xsl:include href="table.xsl" />
</xsl:stylesheet>
