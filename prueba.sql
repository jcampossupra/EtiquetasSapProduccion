ALTER PROCEDURE "SBO_SP_SUPR_OWOR" 
( IN object_type_supr varchar(20), 
  IN transaction_type_supr varchar(1), 
  IN num_of_cols_in_key_supr integer, 
  IN list_of_key_cols_tab_del_supr varchar(255), 
  IN list_of_cols_val_tab_del_supr varchar(255), 
  OUT VP_MSGERROR varchar(255), 
  OUT VP_error integer

)
LANGUAGE SQLSCRIPT 

 AS 
--VARIABLE USADA PARA VALIDAR EL CIERRE CORRECTO DE LAS ORDENES DE PRODUCCIÓN SEGÚN EL CONSUMO DE ACTIVDADES
    EM_ACT NUMERIC (20);
    RE_PT NUMERIC (20);
    
--VARIABLE PARA VALIDAR EL INGRESO DE LA MAQUINA AL CREAR LA ORDEN DE PRODUCCIÓN
    OP_MAQ NUMERIC(2);
        
--VARIABLE USADA PARA VALIDAR EL CORRECTO CIERRE DE LAS ORDENES DE PRODUCCIÓN
    OP_REPP NUMERIC(20);
    OP_COPP NUMERIC(20);
    OP_PP nvarchar(10);
    OP_STATUS nvarchar(1);
    RE NUMERIC (2);
    EM NUMERIC (2);
    OP numeric (10);
    OP_DIGITADOR NVARCHAR(50);
    OP_CPLANIFICADA NUMERIC(10);
    OP_CDIGITADA NUMERIC (10);
    OP_DESPERDICIO NUMERIC (10);
    
--VARIABLE USADA PARA VALIDAR EL INGRESO DEL PEDIDO DE VENTAS EN LA ORDEN DE PRODUCCIÓN
    OP_PED NUMERIC(10);
    OP_PEDCL NVARCHAR(15);
--VARIABLE USADA PARA PERMITIR CERRAR ORDENES DE PRODUCCION POR GRUPO DE ARTICULOS
    OP_GCODE NUMERIC(3);
    
    OP_REPOSICION nvarchar(10);
    OP_SOLICITANTE_REP NVARCHAR(50);
    OP_USERID INT;

--VARIABLE USADA PARA VALIDAR CAMPOS DE UNA OF DE UN PRODUCTO EN PROCESO
    OF_ITEM NVARCHAR(10);
    OF_ANCHO NVARCHAR(15);
    OF_COLOR NVARCHAR(15);
    OF_ESPESOR NVARCHAR(15);
    OF_COLOR_IMP NVARCHAR(15);
    OF_ORIENTACION_IMP NVARCHAR(15);
    OF_DENSIDAD NVARCHAR(15);
    OF_COD_GRUPO_ART INTEGER;
    OF_GRUPO_ART NVARCHAR(50);
    OF_LOGO_INSECT NVARCHAR(15);
    OF_LOGO_PRIM NVARCHAR(15);
    OF_LOGO_SECUN NVARCHAR(15);
    OF_TIPO_TRAT NVARCHAR(15);    
    OF_ITEM2 NVARCHAR(10);
    OF_ANCHO2 NVARCHAR(15);
    OF_COLOR2 NVARCHAR(15);
    OF_ESPESOR2 NVARCHAR(15);
    OF_COLOR_IMP2 NVARCHAR(15);
    OF_ORIENTACION_IMP2 NVARCHAR(15);
    OF_DENSIDAD2 NVARCHAR(15);
    OF_COD_GRUPO_ART2 INTEGER;
    OF_GRUPO_ART2 NVARCHAR(50);
    OF_LOGO_INSECT2 NVARCHAR(15);
    OF_LOGO_PRIM2 NVARCHAR(15);
    OF_LOGO_SECUN2 NVARCHAR(15);
    OF_TIPO_TRAT2 NVARCHAR(15);
    OF_ORDEN_TRABAJO NUMERIC (11);
    OF_BANDERA CHAR;
    OF_CONTADOR INTEGER;
    CantidadBaseOF DOUBLE;
    CantidadMaxLM DOUBLE;
    nroProductoOF NVARCHAR(50);
    origenOF CHAR;     
    contadorPP_OF INTEGER; 
    itemPP_DetalleOF NVARCHAR(50);   
    itemComponenteLM NVARCHAR(50);   
    item_detalleOF NVARCHAR(50); 
    cantidad_requerida DOUBLE; 
    disponible DOUBLE; 
    -----
	TIPO_ARTICULO NVARCHAR(5); 
	-----
	contador_Recur INTEGER;
	/*NUM_OF NVARCHAR(15); 
	CAN_BASE DOUBLE; */    

    --CURSORES ------------------------
    CURSOR C1_OF FOR 
    SELECT a1."ItemCode" FROM OWOR a0 INNER JOIN WOR1 a1 ON a0."DocEntry"=a1."DocEntry" WHERE a0."DocNum"= :OF_ORDEN_TRABAJO;
    
    --Cursor creado por J.Campos 9/21/2023
	--Se añade al cursor el 26/10/2023 Estatus para nuevo bloqueo
	
	CURSOR C2_OF FOR
	SELECT a1."ItemType", a0."DocNum",a1."BaseQty", a0."Status" FROM OWOR a0 INNER JOIN WOR1 a1 ON a0."DocEntry"=a1."DocEntry" WHERE a0."DocEntry" = :list_of_cols_val_tab_del_supr;


/*SELECT T0."DocNum", T1."BaseQty"
 	INTO OF_ORDEN_TRABAJO, CantidadBaseOF
 	FROM OWOR T0
 	INNER JOIN WOR1 T1 ON T0."DocEntry" = T1."DocEntry"
 	WHERE T0."DocEntry"= :list_of_cols_val_tab_del_supr;*/

/*	SELECT T0."ItemType" FROM WOR1 T0 
	INNER JOIN OWOR T1 ON T0."DocEntry" = T1."DocEntry"
	WHERE T0."DocEntry" = :list_of_cols_val_tab_del_supr;
	
*/
    
    
    
    
    -- CURSOR C2_OF FOR 
    -- SELECT a."ItemCode" "item_detalleOF"
    -- , TO_NVARCHAR(SUM(IFNULL(a."PlannedQty",0))) "cantidad_requerida"    
    -- FROM WOR1 a     
    -- WHERE a."DocEntry" = :list_of_cols_val_tab_del_supr AND a."ItemType" = 4
    -- GROUP BY a."ItemCode";
    
    --FIN CURSORES ---------------------
BEGIN

DECLARE EXIT HANDLER FOR SQLEXCEPTION
     BEGIN
        VP_error := ::SQL_ERROR_CODE;
        VP_MSGERROR := N'EXISTE UN PROBLEMA CON EL TRANSACTION NOTIFICATION DE EXX_SALES DE OF. ('|| LEFT(::SQL_ERROR_MESSAGE,50) ||')';
     END;
    
    VP_error := 0;
    VP_MSGERROR := N'Ok';
    
--ENCERO VARIABLES A USAR PARA VALIDAR EL CONSUMO Y RECIBO DE LAS ACTIVIDADES EN LAS ORDENES DE PRODUCCIÓN
EM_ACT :=0;
RE_PT :=0;
--ENCERO VARIABLES A UTILIZAR PARA LA VALIDACIÓN DEL CIERRE DE ORDENES DE PRODUCCIÓN
OP_REPP :=0;
OP_COPP :=0;
OP_PP :='';
OP_STATUS :='';
RE :=0;
EM :=0;
OP :=0;
OP_DIGITADOR:='';

--ENCERO VARIABLES A UTILIZAR PARA LA VALIDACION DE ORDENES DE PRODUCCION
OP_PED :=0;
OP_PEDCL :='';
OP_CPLANIFICADA:=0;
OP_CPLANIFICADA:=0;
OP_DESPERDICIO:=0;
OP_MAQ :=0;
OP_REPOSICION :='';
OP_SOLICITANTE_REP :='';
OP_USERID :=0;

--ENCERO VARIABLES A UTILIZAR PARA VALIDAR CAMPOS DE UNA OF DE UN PRODUCTO EN PROCESO
    OF_ITEM :='';
    OF_ANCHO :='';
    OF_COLOR :='';
    OF_ESPESOR :='';
    OF_COLOR_IMP :='';
    OF_ORIENTACION_IMP :='';
    OF_DENSIDAD :='';
    OF_COD_GRUPO_ART :=0;
    OF_GRUPO_ART :='';
    OF_LOGO_INSECT :='';
    OF_LOGO_PRIM :='';
    OF_LOGO_SECUN :='';
    OF_TIPO_TRAT :='';
    OF_ORDEN_TRABAJO :=0;
    OF_ITEM2 :='';
    OF_ANCHO2 :='';
    OF_COLOR2 :='';
    OF_ESPESOR2 :='';
    OF_COLOR_IMP2 :='';
    OF_ORIENTACION_IMP2 :='';
    OF_DENSIDAD2 :='';
    OF_COD_GRUPO_ART2 :=0;
    OF_GRUPO_ART2 :='';
    OF_LOGO_INSECT2 :='';
    OF_LOGO_PRIM2 :='';
    OF_LOGO_SECUN2 :='';
    OF_TIPO_TRAT2 :='';
    OF_BANDERA :='F';
    OF_CONTADOR :=0;
    CantidadBaseOF :=0;
    CantidadMaxLM :=0;
    nroProductoOF :='';
    origenOF :='';
    contadorPP_OF := 0;
    itemPP_DetalleOF :='';   
    itemComponenteLM :='';
    item_detalleOF :='';
    cantidad_requerida :=0;
    disponible :=0; 
    TIPO_ARTICULO :=0; 
    contador_Recur :=0;
  /*  NUM_OF :=0;   
    CAN_BASE :=0; */
----------------------------------------------------------------------------------------------

/* ALERTAS PARA ORDENES DE PRODUCCIÓN
VP_ERROR es igual al tipo de objeto más un secuencial
SI ES FORMULARIO DE ORDENES DE PRODUCCIÓN TIPO DE OBJETO (202)
SI EL TIPO DE TRANSACCION ES AGREGAR (A) O MODIFICAR (U) */ 
IF :VP_error=0 AND (:object_type_supr='202' AND (:transaction_type_supr='U' OR :transaction_type_supr='A')) THEN  


--Bloqueo creado por J.Campos 9/21/2023  
--Solicitado Por Milton Zambrano
--Validado por milton Sambrano 
--Una orden de fabricacion no puede ser creada si el articulo tiene como cantidad base numeros mayor a 1
--Una Orden de fabricacion no puede ser creada si el recurso en su valor base sea de 0 a 1.5    
 

 
 
 OPEN C2_OF;
 FETCH C2_OF INTO TIPO_ARTICULO, OF_ORDEN_TRABAJO, CantidadBaseOF, OP_STATUS;
 
 	WHILE NOT C2_OF::NOTFOUND DO
 		IF :TIPO_ARTICULO = 4 THEN
 			IF :CantidadBaseOF > 1 THEN
 			VP_error:= 1044;
 			VP_MSGERROR:= 'LA CANTIDAD BASE DEL ARTICULO ES MAYOR A 1... NO SE PUEDE CREAR LA ORDEN DE FABRICACIÓN';
 	        END IF;
 	     END IF;
 	     IF:TIPO_ARTICULO = 290 THEN
 		   IF :CantidadBaseOF < 1.6 THEN
 			VP_error:= 1045;
 			VP_MSGERROR:= 'LA CANTIDAD BASE DEL RECURSO ES MAYOR A 1.5... NO SE PUEDE CREAR LA ORDEN DE FABRICACIÓN';
 		    END IF; 
 		END IF;
--Bloqueo creado por J.Campos 10/26/2023  
--Solicitado Por Milton Zambrano
--Validado por milton Sambrano 
--Bloqueo en Orden de Fabricacion cuando el estado sea liberado y el usuario sea bodega de transito, validar que la OF tenga minimo 2 recursos
 		IF :OP_STATUS = 'R' AND OP_USERID = 152 THEN
 			SELECT SUM(CASE WHEN b."ItemType" = 290 THEN 1 ELSE 0 END )INTO contador_Recur FROM WOR1 b INNER JOIN OWOR a ON b."DocEntry" = a."DocEntry" WHERE a."DocEntry" = :list_of_cols_val_tab_del_supr;
 			IF :contador_Recur < 2 THEN 
 			VP_error:= 1046;
 			VP_MSGERROR:= 'LA CANTIDAD DE RECURSO ES MENOR A 2... NO SE PUEDE ACTUALIZAR LA ORDEN DE FABRICACIÓN';
 		    END IF; 
 			
 		END IF;
 	    FETCH C2_OF INTO TIPO_ARTICULO, OF_ORDEN_TRABAJO, CantidadBaseOF, OP_STATUS;
 	    
 	   END WHILE;
 CLOSE C2_OF; 

    --VERIFICO QUE LA CANTIDAD DIGITADA SEA IGUAL QUE LA CANTIDAD PLANIFICADA TOMANDO EN CUENTA EL DESPERDICIO
    SELECT IFNULL(sum(T1."PlannedQty"),0) INTO OP_DESPERDICIO FROM "OWOR" T0 
    INNER JOIN WOR1 T1 on T0."DocEntry" = T1."DocEntry"
    INNER JOIN OITM T2 on T1."ItemCode" = T2."ItemCode"
    WHERE T0."DocEntry" = :list_of_cols_val_tab_del_supr AND T2."ItemName" Like '%%DESPERDICIO%%';
            
    IF OP_DESPERDICIO>0 THEN
        SELECT IFNULL(T0."PlannedQty",0), IFNULL(sum(T1."PlannedQty"),0) INTO OP_CPLANIFICADA, OP_CDIGITADA FROM "OWOR" T0 
        INNER JOIN WOR1 T1 on T0."DocEntry" = T1."DocEntry"
        INNER JOIN OITM T2 on T1."ItemCode" = T2."ItemCode"
        WHERE T0."DocEntry" = :list_of_cols_val_tab_del_supr AND T1."ItemType" !=290 GROUP BY T0."PlannedQty" ;
    ELSE
        SELECT IFNULL(T0."PlannedQty",0), IFNULL(sum(T1."PlannedQty"),0) INTO OP_CPLANIFICADA, OP_CDIGITADA FROM "OWOR" T0 
        INNER JOIN WOR1 T1 on T0."DocEntry" = T1."DocEntry"
        INNER JOIN OITM T2 on T1."ItemCode" = T2."ItemCode"
        WHERE T0."DocEntry" = :list_of_cols_val_tab_del_supr AND T1."ItemType" !=290 AND T2."ItemName" NOT Like '%%DESPERDICIO%%'
        GROUP BY T0."PlannedQty" ;
    END IF;                    
        
    --OPCION USADA PARA VALIDAR EL CONSUMO DE TODA LA MATERIA PRIMA RELACIONADA AL PEDIDO Y AL ITEM ANTES DE CERRAR LA ORDEN DE FABRICACIÓN DE UN PT
    --OBTENGO LOS DATOS DE LA ORDEN DE FABRICACIÓN CODIGO DEL PRODUCTO EN PROCESO, ESTADO DE LA ORDEN
    --OBTENGO EL PEDIDO RELACIONADO A LA ORDEN DE FABRCIACION EN CASO DE NO EXISTIR ASIGNO EL 0
    --OBTENGO EL CODIGO DEL GRUPO DE PRODUCTO DEL ITEM A FABRICAR
    --OBTENGO EL CLIENTE DEL PEDIDO
    select distinct IFNULL(T0."OriginNum",0), IFNULL(MAX(case when T4."QryGroup5"='Y' and T3."QryGroup4"='Y' THEN T3."ItemCode" end),''),T0."Status",T4."ItmsGrpCod"
    ,T5."CardCode",T0."PlannedQty", T0."U_Tipo", case when length(T0."U_supervisor") >0 THEN 'Y' else 'N' end, T0."UserSign"
    into OP_PED, OP_PP, OP_STATUS,OP_GCODE, OP_PEDCL, OP_CPLANIFICADA,OP_REPOSICION,OP_SOLICITANTE_REP,OP_USERID FROM "OWOR" T0 
    INNER JOIN "OITT" T1 ON T1."Code"= T0."ItemCode"
    INNER JOIN "ITT1" T2 ON T2."Father"= T1."Code"
    INNER JOIN "OITM" T3 ON T3."ItemCode" = T2."Code"
    INNER JOIN "OITM" T4 ON T4."ItemCode" = T0."ItemCode"
    LEFT JOIN "ORDR" T5 ON T5."DocNum"=T0."OriginNum"
    WHERE T0."DocEntry" = :list_of_cols_val_tab_del_supr
    GROUP BY T0."Status",T4."ItmsGrpCod",T5."CardCode",T0."OriginNum",T0."PlannedQty",T0."U_Tipo", T0."U_supervisor",T0."UserSign";
    
    --REALIZO LOS BLOQUEOS SI NO ES ALGUNO DE LOS SIGUIENTES GRUPOS DE ARTICULOS POR SER MP
    --- 242 MP INSECTICIDA, 244 MP PALETIZADO ALTA, 245 MP PALETIZADO BAJA, 248 MP COLORANTES
    -- 256 MD MEZCLADO SOP, 257 INSUMO EMPAQUE, 259 PP AGLUTINADO ALTA, 260 PP AGLUTINADO BAJA 
    -- 264 PP ROLLO EMPAQUE, 306 MP MEZCLA MASTERBACH, 327  MP TINTAS
    --SI NO TIENE PEDIDO ASIGNADO Y NO ES DEL CLIENTE SUPRALIVE ENVIO MENSAJE DE ERROR
    IF  (:OP_PED=0 AND OP_GCODE!= 242 AND OP_GCODE!=244 AND OP_GCODE!= 245 AND OP_GCODE!= 248 AND OP_GCODE!= 256 AND OP_GCODE!= 257 AND OP_GCODE!= 259 AND OP_GCODE!= 260 AND OP_GCODE!= 264 AND OP_GCODE!= 306 AND OP_GCODE!= 327) THEN
        VP_error :=1007;
        VP_MSGERROR :='DEBEN INGRESAR PEDIDO DE VENTA EN CADA ORDEN DE PRODUCCIÓN ... ORDEN DE PRODUCCION MAL INGRESADA';
    END IF;
    
    --SI EL USUARIO ES DE LA BODEGA DE TRANSITO O EL ASISTENTE DE PRODUCCION VALIDO LOS CAMPOS DE REPOSICIÓN
    IF (OP_REPOSICION = 'Reposicion' and OP_USERID !=152 and OP_USERID !=72 and OP_USERID !=72 ) THEN
        VP_error :=1007;
        VP_MSGERROR :='NO TIENE ACCESO PARA CREAR ORDENES DE FABRICACION POR REPOSICION ... ORDEN DE PRODUCCION MAL INGRESADA';
    END IF;
    
    --SI EL USUARIO ES DE LA BODEGA DE TRANSITO NO PERMITO CREAR ORDENES DE FABRICACION CON CANTIDAD MAYOR A 50
    IF (:OP_CPLANIFICADA >50 and OP_USERID =152) OR (:OP_REPOSICION ='Normal' and OP_USERID =152) THEN 
        VP_error :=1007;
        VP_MSGERROR :='SOLO TIENE ACCESO A CREAR ORDENES DE FABRICACION POR REPOSICION CON CANTIDAD MENOR O IGUAL A 50 ... ORDEN DE PRODUCCION MAL INGRESADA';
    END IF;
            
    --SI LA ORDEN ES DE TIPO REPOSICION DEBEN UBICAR EL SOLICITANTE (SUPERVISOR)
    IF (:OP_REPOSICION ='Reposicion' and OP_SOLICITANTE_REP='N' ) THEN 
        VP_error :=1007;
        VP_MSGERROR :='DEBE INGRESAR EL SOLICITANTE DE LA REPOSICION ... ORDEN DE PRODUCCION MAL INGRESADA';
    END IF;
        
                   
    -- Solicitado por Milton Zambrano
    -- Validado por Euler Pinargote                                         
    
    --ALERTA PARA EVITAR CREAR OF DE PT DONDE EN LOS COMPONENTES EL PP NO DEBE TENER LA CANTIDAD BASE SUPERIOR AL DOBLE DE LA CANTIDAD DE LA LISTA DE MATERIALES        
    SELECT a."ItemCode" "nroProductoOF", a."OriginType" "origenOF", SUM(CASE WHEN b."ItemCode" LIKE 'PP%%%%' THEN 1 ELSE 0 END) "itemPP_OF" INTO nroProductoOF, origenOF, contadorPP_OF FROM OWOR a INNER JOIN WOR1 b ON a."DocEntry" = b."DocEntry" WHERE a."DocEntry" = :list_of_cols_val_tab_del_supr GROUP BY a."ItemCode", a."OriginType";                                              
                    
    --PRIMERO VERIFICO QUE EL ITEM A FABRICAR SEA PT, LUEGO SU ORIGEN DE CREACIÓN DEBE SER MANUAL(M), POR ÚLTIMO VALIDO QUE EN LOS COMPONENTES TENGA POR UN PP 
    IF UPPER(SUBSTR(:nroProductoOF,0,2)) = 'PT' AND :origenOF = 'M' AND :contadorPP_OF = 1 THEN
            
        SELECT a."ItemCode" "itemPP_DetalleOF", c."Code" "itemComponenteLM" INTO itemPP_DetalleOF, itemComponenteLM 
        FROM WOR1 a INNER JOIN OWOR b ON a."DocEntry" = b."DocEntry" INNER JOIN ITT1 c ON b."ItemCode" = c."Father" AND c."Code" LIKE 'PP%%%%'
        WHERE a."DocEntry" = :list_of_cols_val_tab_del_supr AND a."ItemCode" LIKE 'PP%%%%' AND c."Father" = :nroProductoOF;
        
        --VERIFIO QUE EL PP DE LA OF SEA IGUAL AL PP DE LA LISTA DE MATERIALES
        IF :itemPP_DetalleOF = :itemComponenteLM  THEN  
                
            SELECT IFNULL(a."BaseQty",0) "Cantidad Base OF", IFNULL((c."Quantity"*2),0) "Cantidad Máxima L/M" INTO CantidadBaseOF, CantidadMaxLM FROM WOR1 a 
            INNER JOIN OWOR b ON a."DocEntry" = b."DocEntry" AND b."OriginType" = 'M' AND b."ItemCode" LIKE 'PT%%%%%' 
            INNER JOIN ITT1 c ON b."ItemCode" = c."Father" AND c."Code" LIKE 'PP%%%%%'
            WHERE a."DocEntry" = :list_of_cols_val_tab_del_supr AND a."ItemCode" LIKE 'PP%%%%%';
            
            --VERIFICO QUE CANTIDAD DE LA OF NO EXCEDA LA CANTIDAD MAXIMA PERMITIDA DE LA LISTA DE MATERIALES
            IF :CantidadBaseOF > :CantidadMaxLM THEN 
                VP_error := 1044;
                VP_MSGERROR := 'La cantidad base: ' || :CantidadBaseOF || '  supera el máximo permitido en base a la lista de materiales del producto a fabricar: ' || :CantidadMaxLM || ' SUPR_OWOR..';
            END IF; 
                    
        END IF;
                                    
    END IF;
            
    SELECT COUNT(k0."DocEntry") INTO OF_CONTADOR FROM OWOR k0 WHERE k0."DocEntry" = :list_of_cols_val_tab_del_supr AND UPPER(k0."ItemCode") like 'PP%';         
    
    IF :OF_CONTADOR > 0 THEN
        
        SELECT  IFNULL(a0."ItemCode",''), IFNULL(a1."U_EXX_ANCHO",''), IFNULL(a1."U_EXX_COLOR",''), IFNULL(a1."U_EXX_ESPESOR_MM",''), IFNULL(a1."U_EXX_CIMPRES",''), IFNULL(a1."U_EXX_SENCIREL",''), IFNULL(a1."U_EXX_DENS",''), IFNULL(a1."ItmsGrpCod",0), IFNULL(SUBSTRING(a3."ItmsGrpNam", 4, LENGTH(a3."ItmsGrpNam")),''), IFNULL(a1."U_EXX_LOGO_INSECT",''), IFNULL(a1."U_EXX_LOGO_PRI",''), IFNULL(a1."U_EXX_LOGO_SEC",''), IFNULL(a1."U_EXX_TIPO_TRATAMIENTO",''), IFNULL(a0."U_OrdenTrabajo",0)
        INTO OF_ITEM, OF_ANCHO, OF_COLOR, OF_ESPESOR, OF_COLOR_IMP, OF_ORIENTACION_IMP, OF_DENSIDAD, OF_COD_GRUPO_ART, OF_GRUPO_ART, OF_LOGO_INSECT,  OF_LOGO_PRIM, OF_LOGO_SECUN, OF_TIPO_TRAT, OF_ORDEN_TRABAJO
        FROM OWOR a0
        INNER JOIN OITM a1 ON a0."ItemCode" = a1."ItemCode" 
        INNER JOIN OITB a3 ON a1."ItmsGrpCod" = a3."ItmsGrpCod"
        WHERE a0."DocEntry" = :list_of_cols_val_tab_del_supr;
                    
        IF :OF_ORDEN_TRABAJO <> 0 AND UPPER(:OF_ITEM) LIKE 'PP%' THEN
                                
            OPEN C1_OF;           
                FETCH  C1_OF INTO OF_ITEM2;        
                WHILE NOT C1_OF::NOTFOUND DO            
                    IF :OF_ITEM2 = :OF_ITEM THEN              
                        OF_BANDERA := 'T';           
                    END IF;                                                       
                FETCH  C1_OF INTO OF_ITEM2;                
                END WHILE;
            
                IF :OF_BANDERA = 'T' THEN
                    SELECT IFNULL(a1."ItemCode",'')
                    , IFNULL(a1."U_EXX_ANCHO",'')
                    , IFNULL(a1."U_EXX_COLOR",'')
                    , IFNULL(a1."U_EXX_ESPESOR_MM",'')
                    , IFNULL(a1."U_EXX_CIMPRES",'')
                    , IFNULL(a1."U_EXX_SENCIREL",'')
                    , IFNULL(a1."U_EXX_DENS",'')
                    , IFNULL(a1."ItmsGrpCod",0)
                    , IFNULL(SUBSTRING(a3."ItmsGrpNam", 4, LENGTH(a3."ItmsGrpNam")),'')
                    , IFNULL(a1."U_EXX_LOGO_INSECT",'')
                    , IFNULL(a1."U_EXX_LOGO_PRI",'')
                    , IFNULL(a1."U_EXX_LOGO_SEC",'')
                    , IFNULL(a1."U_EXX_TIPO_TRATAMIENTO",'')
                    INTO 
                    OF_ITEM2,
                    OF_ANCHO2,
                    OF_COLOR2,
                    OF_ESPESOR2,
                    OF_COLOR_IMP2,
                    OF_ORIENTACION_IMP2,
                    OF_DENSIDAD2,
                    OF_COD_GRUPO_ART2,
                    OF_GRUPO_ART2,
                    OF_LOGO_INSECT2,
                    OF_LOGO_PRIM2,
                    OF_LOGO_SECUN2,
                    OF_TIPO_TRAT2                       
                    FROM OWOR a2   
                    INNER JOIN OITM a1 ON a1."ItemCode" = a2."ItemCode" and a2."DocNum" = :OF_ORDEN_TRABAJO
                    INNER JOIN OITB a3 ON a1."ItmsGrpCod" = a3."ItmsGrpCod";
                                                
                    IF :OF_ANCHO != :OF_ANCHO2 THEN
                        --En los grupos de articulos de Cluster el ancho no es igual por eso se toma en cuenta
                        IF ((:OF_ANCHO = '-' AND :OF_ANCHO2 = '') OR (:OF_ANCHO = '' AND :OF_ANCHO2 = '-')) OR (:OF_COD_GRUPO_ART = '341' OR :OF_COD_GRUPO_ART = '356') THEN
                        --Valido las excepciones solicitadas por Euler 
                        ELSE
                            VP_error :=1032;
                            VP_MSGERROR := 'EL ÍTEM: ' || :OF_ITEM2 || '  NO COINCIDE CON EL ANCHO DEL ÍTEM: ' || :OF_ITEM || '  NO SE PUEDE CREAR LA ORDEN DE FABRICACIÓN..'; 
                        END IF;               
                    END IF;
                            
                    IF :OF_COLOR != :OF_COLOR2 THEN   
                        --Valido los colores y permito los que son lo mismo pero distinto codigo           
                        IF ((:OF_COLOR = '32' AND :OF_COLOR2 = '10') OR (:OF_COLOR = '10' AND :OF_COLOR2 = '32'))
                            OR ((:OF_COLOR = '29' AND :OF_COLOR2 = '04') OR (:OF_COLOR = '04' AND :OF_COLOR2 = '29'))
                            OR ( (:OF_COLOR = '22' AND :OF_COLOR2 = '27') OR (:OF_COLOR = '27' AND :OF_COLOR2 = '22')) 
                            OR ((:OF_COLOR = '15' OR :OF_COLOR = '40' OR :OF_COLOR = '24' OR :OF_COLOR = '20')
                            AND (:OF_COLOR2 = '15' OR :OF_COLOR2 = '40' OR :OF_COLOR2 = '24' OR :OF_COLOR2 = '20')) 
                            OR ((:OF_COLOR = '-' AND :OF_COLOR2 = '') OR (:OF_COLOR = '' AND :OF_COLOR2 = '-')) THEN                       
                            --Valido las excepciones solicitadas por Euler   
                        ELSE                                      
                            VP_error :=1033;
                            VP_MSGERROR := 'EL ÍTEM: ' || :OF_ITEM2 || '  NO COINCIDE CON EL COLOR DE FUNDA DEL ÍTEM: ' || :OF_ITEM || '  NO SE PUEDE CREAR LA ORDEN DE FABRICACIÓN..';                
                        END IF;     
                
                    END IF;
                            
                    IF :OF_ESPESOR != :OF_ESPESOR2 THEN
                        IF ((:OF_ESPESOR = '-' AND :OF_ESPESOR2 = '') OR (:OF_ESPESOR = '' AND :OF_ESPESOR2 = '-')) THEN
                        --Valido las excepciones solicitadas por Euler 
                        ELSE
                            VP_error :=1034;
                            VP_MSGERROR := 'EL ÍTEM: ' || :OF_ITEM2 || '  NO COINCIDE CON EL ESPESOR DEL ÍTEM: ' || :OF_ITEM || '  NO SE PUEDE CREAR LA ORDEN DE FABRICACIÓN..';
                        END IF;
                    END IF;
                
                    IF :OF_COLOR_IMP != :OF_COLOR_IMP2 THEN
                        -- -Valido los colores de impresion y permito los que son lo mismo pero distinto codigo                
                        IF ((:OF_COLOR_IMP = '-' AND :OF_COLOR_IMP2 = '') OR (:OF_COLOR_IMP = '' AND :OF_COLOR_IMP2 = '-')) 
                            OR ((:OF_COLOR_IMP = '01' AND :OF_COLOR_IMP2 = '08') OR (:OF_COLOR_IMP = '08' AND :OF_COLOR_IMP2 = '01'))
                            OR ((:OF_COLOR_IMP = '04' AND :OF_COLOR_IMP2 = '15') OR (:OF_COLOR_IMP = '15' AND :OF_COLOR_IMP2 = '04'))
                            OR ( (:OF_COLOR_IMP = '02' AND :OF_COLOR_IMP2 = '10') OR (:OF_COLOR_IMP = '10' AND :OF_COLOR_IMP2 = '02'))  THEN                                 
                        --Valido las excepciones solicitadas por Euler 
                        ELSE
                            VP_error :=1035;
                            VP_MSGERROR := 'EL ÍTEM: ' || :OF_ITEM2 || '  NO COINCIDE CON EL COLOR IMPRESION DEL ÍTEM: ' || :OF_ITEM || '  NO SE PUEDE CREAR LA ORDEN DE FABRICACIÓN..';
                        END IF;
                    END IF;
                
                    IF :OF_ORIENTACION_IMP != :OF_ORIENTACION_IMP2 THEN
                        IF ((:OF_ORIENTACION_IMP = '-' AND :OF_ORIENTACION_IMP2 = '') 
                        OR (:OF_ORIENTACION_IMP = '' AND :OF_ORIENTACION_IMP2 = '-')) 
                        OR (:OF_COD_GRUPO_ART = '344' OR :OF_COD_GRUPO_ART = '345' 
                        OR :OF_COD_GRUPO_ART = '362'  OR :OF_COD_GRUPO_ART = '347' 
                        OR :OF_COD_GRUPO_ART = '370' OR :OF_COD_GRUPO_ART = '357' 
                        OR :OF_COD_GRUPO_ART = '363' OR :OF_COD_GRUPO_ART = '346' ) THEN
                        --Valido las excepciones solicitadas por Euler 
                        ELSE
                            VP_error :=1036;
                            VP_MSGERROR := 'EL ÍTEM: ' || :OF_ITEM2 || '  NO COINCIDE CON EL SENTIDO DEL CIREL DEL ÍTEM: ' || :OF_ITEM || '  NO SE PUEDE CREAR LA ORDEN DE FABRICACIÓN..';
                        END IF;
                    END IF;
                
                    IF :OF_DENSIDAD != :OF_DENSIDAD2 THEN
                        IF ((:OF_DENSIDAD = '-' AND :OF_DENSIDAD2 = '') OR (:OF_DENSIDAD = '' AND :OF_DENSIDAD2 = '-')) THEN
                        --Valido las excepciones solicitadas por Euler 
                        ELSE
                            VP_error :=1037;
                            VP_MSGERROR := 'EL ÍTEM: ' || :OF_ITEM2 || '  NO COINCIDE CON EL DENSIDAD DEL ÍTEM: ' || :OF_ITEM || '  NO SE PUEDE CREAR LA ORDEN DE FABRICACIÓN..';
                        END IF;
                    END IF;
                
                    -- El grupo de articulo si el nombre no es igual se permite las siguientes exepciones:
                    -- En los PP para Imprimir siempre va a tener al final "P IM" el resto debe coincidir 
                    -- En ciertos PP tienen al final "IMPR" el resto debe coincidir 
                    IF :OF_GRUPO_ART != :OF_GRUPO_ART2 THEN
                    --Valido grupo entre PP a PT            
                    --  IF (:OF_COD_GRUPO_ART = 329 and :OF_COD_GRUPO_ART2 = 332 )
                    --     OR (:OF_COD_GRUPO_ART = 328 and :OF_COD_GRUPO_ART2 = 331 ) 
                    --     OR (:OF_COD_GRUPO_ART = 330 and :OF_COD_GRUPO_ART2 = 333 )
                    --     OR (:OF_COD_GRUPO_ART = 350 and :OF_COD_GRUPO_ART2 = 349 )
                    --     OR (:OF_COD_GRUPO_ART = 275 and :OF_COD_GRUPO_ART2 = 284 )
                        -- Valido grupos entre PP a PP
                    --     OR (:OF_COD_GRUPO_ART = 344 and :OF_COD_GRUPO_ART2 = 329)
                    --     OR (:OF_COD_GRUPO_ART = 345 and :OF_COD_GRUPO_ART2 = 328 )
                    --     OR (:OF_COD_GRUPO_ART = 362 and :OF_COD_GRUPO_ART2 = 360 )
                    --     OR (:OF_COD_GRUPO_ART = 347 and :OF_COD_GRUPO_ART2 = 341 )
                    --     OR (:OF_COD_GRUPO_ART = 370 and :OF_COD_GRUPO_ART2 = 369 )
                    --     OR (:OF_COD_GRUPO_ART = 357 and :OF_COD_GRUPO_ART2 = 356 )
                    --     OR (:OF_COD_GRUPO_ART = 363 and :OF_COD_GRUPO_ART2 = 361 )
                    --     OR (:OF_COD_GRUPO_ART = 346 and :OF_COD_GRUPO_ART2 = 330 ) THEN
                        IF ( SUBSTRING(:OF_COD_GRUPO_ART, LENGTH(:OF_COD_GRUPO_ART) - 4, LENGTH(:OF_COD_GRUPO_ART) ) = 'P IM' )  THEN  
                            IF ( SUBSTRING(:OF_COD_GRUPO_ART, 0, LENGTH(:OF_COD_GRUPO_ART) - 7) != :OF_GRUPO_ART2 ) 
                                OR ( :OF_GRUPO_ART != SUBSTRING(:OF_COD_GRUPO_ART2, 0, LENGTH(:OF_COD_GRUPO_ART2) - 7) ) 
                                OR ( SUBSTRING(:OF_COD_GRUPO_ART, 0, LENGTH(:OF_COD_GRUPO_ART) - 7) != SUBSTRING(:OF_COD_GRUPO_ART2, 0, LENGTH(:OF_COD_GRUPO_ART2) - 7) ) THEN                        
                                --Valido las excepciones solicitadas por Euler 
                            ELSE
                                VP_error :=1038;
                                VP_MSGERROR := 'EL ÍTEM: ' || :OF_ITEM2 || '  NO COINCIDE CON EL GRUPO DE ARTICULO DEL ÍTEM: ' || :OF_ITEM || '  NO SE PUEDE CREAR LA ORDEN DE FABRICACIÓN..';
                            END IF; 
                        END IF;      
                    END IF;
                
                    IF :OF_LOGO_INSECT != :OF_LOGO_INSECT2 THEN
                        IF ((:OF_LOGO_INSECT = '-' AND :OF_LOGO_INSECT2 = '') OR (:OF_LOGO_INSECT = '' AND :OF_LOGO_INSECT2 = '-')) THEN
                        --Valido las excepciones solicitadas por Euler 
                        ELSE
                            VP_error :=1039;
                            VP_MSGERROR := 'EL ÍTEM: ' || :OF_ITEM2 || '  NO COINCIDE CON EL LOGO INSECTICIDA DEL ÍTEM: ' || :OF_ITEM || '  NO SE PUEDE CREAR LA ORDEN DE FABRICACIÓN..';
                        END IF;
                    END IF;
                
                    IF :OF_LOGO_PRIM != :OF_LOGO_PRIM2 THEN
                        IF ((:OF_LOGO_PRIM = '-' AND :OF_LOGO_PRIM2 = '') OR (:OF_LOGO_PRIM = '' AND :OF_LOGO_PRIM2 = '-')) THEN
                            --Valido las excepciones solicitadas por Euler 
                        ELSE
                            VP_error :=1040;
                            VP_MSGERROR := 'EL ÍTEM: ' || :OF_ITEM2 || '  NO COINCIDE CON EL LOGO PRIMARIO DEL ÍTEM: ' || :OF_ITEM || '  NO SE PUEDE CREAR LA ORDEN DE FABRICACIÓN..';
                        END IF;
                    END IF;             
                    
                    IF :OF_LOGO_SECUN != :OF_LOGO_SECUN2 THEN                
                        IF ((:OF_LOGO_SECUN = '-' AND :OF_LOGO_SECUN2 = '') OR (:OF_LOGO_SECUN = '' AND :OF_LOGO_SECUN2 = '-')) THEN
                            --Valido las excepciones solicitadas por Euler 
                        ELSE
                            VP_error :=1041;
                            VP_MSGERROR := 'EL ÍTEM: ' || :OF_ITEM2 || '  NO COINCIDE CON EL LOGO SECUNDARIO DEL ÍTEM: ' || :OF_ITEM || '  NO SE PUEDE CREAR LA ORDEN DE FABRICACIÓN..';
                        END IF;
                
                    END IF;           
                                                                                        
                ELSE
                    VP_error :=1043;
                    VP_MSGERROR := 'EL ÍTEM: ' || :OF_ITEM || '  NO CONSTA EN LA ORDEN DE TRABAJO ASIGNADA...  NO SE PUEDE CREAR LA ORDEN DE FABRICACIÓN..';
                END IF;
        
            CLOSE C1_OF;  
           

              
                  
END IF;                           
        END IF; 
        
        /*    
        --P = Planificada 
        IF :VP_error= 0 AND :OP_STATUS='P' THEN 
            OPEN C2_OF;           
                FETCH C2_OF INTO item_detalleOF, cantidad_requerida;                                            
                    
                WHILE NOT C2_OF::NOTFOUND DO   

                    SELECT TO_NVARCHAR(((IFNULL(b."OnHand",0) + IFNULL(b."OnOrder",0)) - IFNULL(b."IsCommited",0))) "disponible" INTO disponible FROM 
                    OITM b WHERE b."ItemCode" = :item_detalleOF;

                    IF (:disponible - :cantidad_requerida) < 0   THEN 
                        VP_error := 20201;
                        VP_MSGERROR := 'La cantidad requerida(' || :cantidad_requerida || ') del ítem(' || :item_detalleOF || ') supera lo disponible(' || :disponible || ') .. SUPR_OWOR';
                    END IF;

                FETCH C2_OF INTO item_detalleOF, cantidad_requerida;  
 
                END WHILE;
            CLOSE C2_OF;  
        END IF;
        */
 
        
END IF;  


END;