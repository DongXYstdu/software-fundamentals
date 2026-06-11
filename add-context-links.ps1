# PowerShell script to add prev/next context links to all markdown posts
# Groups articles by primary category and adds navigation links

$postsDir = "d:\work\docs\software-fundamentals\_posts"
$files = Get-ChildItem -Path $postsDir -Filter "*.md"

# Parse all articles
$articles = @()
foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw -Encoding UTF8
    
    # Extract categories from front matter
    if ($content -match '---\r?\n(.*?)---\r?\n' -SingleLine) {
        $frontMatter = $Matches[1]
        
        # Get title
        $title = ''
        if ($frontMatter -match 'title:\s*(.+)') {
            $title = $Matches[1].Trim()
        }
        
        # Get categories
        $categories = @()
        if ($frontMatter -match 'categories:\s*\[(.+?)\]') {
            $catStr = $Matches[1]
            $categories = ($catStr -split ',') | ForEach-Object { $_.Trim() }
        }
        
        # Get primary category (first one)
        $primaryCat = if ($categories.Count -gt 0) { $categories[0] } else { "未分类" }
        
        # Get URL slug (filename without .md)
        $slug = $file.Name -replace '\.md$', ''
        
        $articles += [PSCustomObject]@{
            File = $file.FullName
            Name = $file.Name
            Title = $title
            PrimaryCat = $primaryCat
            Slug = $slug
            Content = $content
        }
    }
}

# Group by primary category and sort by slug
$groups = $articles | Group-Object PrimaryCat

foreach ($group in $groups) {
    $sortedArticles = $group.Group | Sort-Object Slug
    
    for ($i = 0; $i -lt $sortedArticles.Count; $i++) {
        $article = $sortedArticles[$i]
        
        # Determine prev and next
        $prevArticle = if ($i -gt 0) { $sortedArticles[$i - 1] } else { $null }
        $nextArticle = if ($i -lt $sortedArticles.Count - 1) { $sortedArticles[$i + 1] } else { $null }
        
        # Build context links HTML
        $contextLinks = ""
        if ($prevArticle -or $nextArticle) {
            $prevLink = if ($prevArticle) {
                "<a class='context-link prev' href='/software-fundamentals/posts/$($prevArticle.Slug)/'><span class='context-label'>上一篇</span><span class='context-title'>$($prevArticle.Title)</span></a>"
            } else {
                "<a class='context-link prev disabled'><span class='context-label'>上一篇</span><span class='context-title'>暂无</span></a>"
            }
            
            $nextLink = if ($nextArticle) {
                "<a class='context-link next' href='/software-fundamentals/posts/$($nextArticle.Slug)/'><span class='context-label'>下一篇</span><span class='context-title'>$($nextArticle.Title)</span></a>"
            } else {
                "<a class='context-link next disabled'><span class='context-label'>下一篇</span><span class='context-title'>暂无</span></a>"
            }
            
            $contextLinks = "`n<div class='context-nav'>$prevLink`n$nextLink`n</div>`n"
        }
        
        # Check if context links already exist
        if ($article.Content -notmatch '<div class=''context-nav''>') {
            $newContent = $article.Content + $contextLinks
            [System.IO.File]::WriteAllText($article.File, $newContent, [System.Text.Encoding]::UTF8)
            Write-Output "Updated: $($article.Name)"
        } else {
            Write-Output "Skip (already has context): $($article.Name)"
        }
    }
}

Write-Output "`nDone! Processed $($articles.Count) articles in $($groups.Count) categories."
