-- Part 3: Views, Functions, Cursor, Summary
-- TEST 10: View v_BaoCaoDoanhThuTheoThang
SET @TestName=N'View: v_BaoCaoDoanhThuTheoThang';
BEGIN TRY
    SELECT @RowCount=COUNT(*) FROM dbo.v_BaoCaoDoanhThuTheoThang;
    IF @RowCount>=0 SET @Result=1 ELSE SET @Result=0;
END TRY BEGIN CATCH SET @Result=0; END CATCH
IF @Result=1 BEGIN PRINT N'[PASS] '+@TestName; SET @PassCount+=1; END ELSE BEGIN PRINT N'[FAIL] '+@TestName; SET @FailCount+=1; END
SET @TestCount+=1;

-- TEST 11: Function fn_TinhGiamGiaVoucher
SET @TestName=N'Function: fn_TinhGiamGiaVoucher';
BEGIN TRY
    SET @Disc=dbo.fn_TinhGiamGiaVoucher('WELCOME10',500000);
    IF @Disc=50000 SET @Result=1 ELSE SET @Result=0;
END TRY BEGIN CATCH SET @Result=0; END CATCH
IF @Result=1 BEGIN PRINT N'[PASS] '+@TestName; SET @PassCount+=1; END ELSE BEGIN PRINT N'[FAIL] '+@TestName; SET @FailCount+=1; END
SET @TestCount+=1;

-- TEST 12: Cursor sp_Cursor_QuetDonQuocHan
SET @TestName=N'Cursor: sp_Cursor_QuetDonQuocHan';
BEGIN TRY
    EXEC dbo.sp_Cursor_QuetDonQuocHan @TimeoutHours=24; SET @Result=1;
END TRY BEGIN CATCH SET @Result=0; END CATCH
IF @Result=1 BEGIN PRINT N'[PASS] '+@TestName; SET @PassCount+=1; END ELSE BEGIN PRINT N'[FAIL] '+@TestName; SET @FailCount+=1; END
SET @TestCount+=1;

-- SUMMARY
PRINT N''; PRINT N'============================================================';
PRINT N'=== KẾT QUẢ TỔNG HỢP ===';
PRINT N'============================================================';
PRINT N'Tổng test: '+CAST(@TestCount AS NVARCHAR)+N', Passed: '+CAST(@PassCount AS NVARCHAR)+N', Failed: '+CAST(@FailCount AS NVARCHAR);
IF @FailCount=0 PRINT N'🎉 TẤT CẢ TEST ĐÃ PASS!'; ELSE PRINT N'⚠️ CÓ '+CAST(@FailCount AS NVARCHAR)+N' TEST FAILED.';
PRINT N'============================================================';