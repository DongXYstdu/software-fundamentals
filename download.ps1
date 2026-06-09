$urls = @(
    @{url="https://xiaolincoding.com/mysql/base/how_select.html"; title="执行一条 SQL 查询语句，期间发生了什么？"; short="SQL查询执行过程"},
    @{url="https://xiaolincoding.com/mysql/base/row_format.html"; title="MySQL 一行记录是怎么存储的？"; short="行记录存储"},
    @{url="https://xiaolincoding.com/mysql/index/index_interview.html"; title="索引常见面试题"; short="索引面试题"},
    @{url="https://xiaolincoding.com/mysql/index/page.html"; title="从数据页的角度看 B+ 树"; short="数据页B+树"},
    @{url="https://xiaolincoding.com/mysql/index/why_index_chose_bpuls_tree.html"; title="为什么 MySQL 采用 B+ 树作为索引？"; short="B+树索引"},
    @{url="https://xiaolincoding.com/mysql/index/2000w.html"; title="MySQL 单表不要超过 2000W 行，靠谱吗？"; short="单表2000W"},
    @{url="https://xiaolincoding.com/mysql/index/index_lose.html"; title="索引失效有哪些？"; short="索引失效"},
    @{url="https://xiaolincoding.com/mysql/index/count.html"; title="count(*) 和 count(1) 有什么区别？哪个性能最好？"; short="count性能"},
    @{url="https://xiaolincoding.com/mysql/index/limit.html"; title="MySQL 分页有什么性能问题？怎么优化？"; short="分页优化"},
    @{url="https://xiaolincoding.com/mysql/transaction/mvcc.html"; title="事务隔离级别是怎么实现的？"; short="事务隔离级别"},
    @{url="https://xiaolincoding.com/mysql/transaction/phantom.html"; title="MySQL 可重复读隔离级别，完全解决幻读了吗？"; short="幻读"},
    @{url="https://xiaolincoding.com/mysql/lock/mysql_lock.html"; title="MySQL 有哪些锁？"; short="MySQL锁"},
    @{url="https://xiaolincoding.com/mysql/lock/how_to_lock.html"; title="MySQL 是怎么加锁的？"; short="加锁机制"},
    @{url="https://xiaolincoding.com/mysql/lock/update_index.html"; title="update 没加索引会锁全表吗？"; short="update无索引"},
    @{url="https://xiaolincoding.com/mysql/lock/lock_phantom.html"; title="MySQL 记录锁+间隙锁可以防止删除操作而导致的幻读吗？"; short="间隙锁幻读"},
    @{url="https://xiaolincoding.com/mysql/lock/deadlock.html"; title="MySQL 死锁了，怎么办？"; short="死锁"},
    @{url="https://xiaolincoding.com/mysql/lock/show_lock.html"; title="加了什么锁，导致死锁的？"; short="死锁分析"},
    @{url="https://xiaolincoding.com/mysql/log/how_update.html"; title="undo log、redo log、binlog 有什么用？"; short="日志机制"},
    @{url="https://xiaolincoding.com/mysql/buffer_pool/buffer_pool.html"; title="揭开 Buffer_Pool 的面纱"; short="BufferPool"},
    @{url="https://xiaolincoding.com/mysql/architecture/mysql_architecture.html"; title="MySQL的架构是怎样的？"; short="MySQL架构"}
)

$tmpDir = "d:\work\docs\software-fundamentals\_tmp_html"
New-Item -ItemType Directory -Path $tmpDir -Force | Out-Null

$headers = @{"User-Agent" = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

for ($i = 0; $i -lt $urls.Length; $i++) {
    $item = $urls[$i]
    $safeTitle = $item.short -replace '[\\/:*?"<>|]', ''
    $htmlFile = Join-Path $tmpDir ("{0:00}_{1}.html" -f ($i+1), $safeTitle)
    
    if (Test-Path $htmlFile -and (Get-Item $htmlFile).Length -gt 5000) {
        Write-Host "[$($i+1)/20] $($item.short) - 缓存命中"
        continue
    }
    
    Write-Host "[$($i+1)/20] $($item.short) - 下载中..."
    try {
        $response = Invoke-WebRequest -Uri $item.url -Headers $headers -TimeoutSec 60 -UseBasicParsing
        [System.IO.File]::WriteAllText($htmlFile, $response.Content, [System.Text.Encoding]::UTF8)
        Write-Host "  完成: $((Get-Item $htmlFile).Length) bytes"
    } catch {
        Write-Host "  失败: $($_.Exception.Message)"
    }
}

Write-Host "`n=== 下载完成 ==="
Get-ChildItem $tmpDir -Filter "*.html" | Select-Object Name, Length
