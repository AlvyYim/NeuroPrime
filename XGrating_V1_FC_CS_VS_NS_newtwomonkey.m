
clear;clc

    mdV1FCneuTTCb= [];
      mdV1FCpuffTTCb= [];

       mdV1FixneuTTC=[];
      mdV1FixpuffTTC=[];
      
       mdV1ori=[];
for mmon=1:1
     mmdV1FCneuTTCb= [];
      mmdV1FCpuffTTCb= [];

       mmdV1FixneuTTC=[];
      mmdV1FixpuffTTC=[];
      
       mmdV1ori=[];
    if mmon==1
folderlist={
% 'F:\COCO\231008';

% 
% 'F:\COCO\230930';
% % 'F:\COCO\231009';
% 'F:\COCO\231012';
% % 'F:\COCO\231020';
% % 'F:\COCO\231028';
% % 'F:\COCO\231027';
% % 'F:\COCO\231024';
% 
% % 'F:\COCO\231012';

% 'F:\COCO\231022';
% 'F:\COCO\231023';
% 'F:\COCO\231024';
% 'F:\COCO\231026';
% 'F:\COCO\231027';
% 
% 'F:\COCO\231109';
% 'F:\COCO\231110';
% 'F:\COCO\231113';
% 'F:\COCO\231114';
% 'F:\COCO\231119';
% 'F:\COCO\231121';



% 'F:\COCO\231214';
% 'F:\COCO\231231';
% 'F:\COCO\231227';
% 'F:\COCO\231231';
% 'F:\COCO\231229';

% 'F:\COCO\240128';
% 'F:\COCO\240129';

% 'F:\COCO\240111';
% 'F:\COCO\240112';
% 'F:\COCO\240114';
% 'F:\COCO\240115';
% 'F:\COCO\240116';

% 'F:\COCO\240124';
% 'F:\COCO\240125';


%%% days of pretest no water
% %45deg puff
'F:\COCO\231227';
'F:\COCO\231228';
% 'F:\COCO\231229';
% 'F:\COCO\231231';%buyaoxiaoguogenghao
% % % % % % % % % % % % 
% % % % % % % % % % 'F:\COCO\240128';
% % % % % % % % % % % % % 'F:\COCO\240129';
% % % % % % % % % % % % % 'F:\COCO\240130';
% % % % % % % % % % % % 
% % % % % % % % % % % % % % 'F:\COCO\231231';
% % % % % % % % % % % % % % 'F:\COCO\240102';
% % % % % % % % % % % % %%135deg puff
% % %%%% 'F:\COCO\240111';
% 'F:\COCO\240112'; %buyaoxiaoguogenghao
% 'F:\COCO\240114';
% 'F:\COCO\240115';
% 'F:\COCO\240116';
% 'F:\COCO\240117';
};
% 'F:\COCO\240117';
% 'F:\COCO\240118';

% 'F:\COCO\240124';
% 'F:\COCO\240125';

%%45puff yami

    else
% % % 
folderlist={
    'F:\Yami\240627';
'F:\Yami\240628';  %
'F:\Yami\240630';  
'F:\Yami\240701';
% 'F:\Yami\240702';
% % % % % % % % % 
% % % % % % % % %%135puff yami  all good
'F:\Yami\240704';  %
'F:\Yami\240705';  %
'F:\Yami\240706';  %
'F:\Yami\240708';
% 'F:\Yami\240709';


%%% days of pretest water
%%45deg puff
% 'F:\COCO\240305';
% 'F:\COCO\240306';
% 'F:\COCO\240307';
%%135deg puff
% 'F:\COCO\240308';
% 'F:\COCO\240310';
% 'F:\COCO\240311';
%%%%%%
% 'F:\Yami\240923';
% 'F:\Yami\240924';
% 'F:\Yami\240926';
% 'F:\Yami\240927';
% 'F:\Yami\240928';

% 'F:\Yami\240930';
% 'F:\Yami\241001';
% 'F:\Yami\241002';
% 'F:\Yami\241003';
% 'F:\Yami\241005';



    };
    end

norn=0;

norwin=100:200;

    
if mmon==1
monkeyID=1;  %%1 coco  2 yami
selcell={'F:\COCO\V1grating_3std.mat'};
repeatday=2; %%when mstd  half+1  45puff 2 38cell 135 2 38c  135 mst1 4 47 
useday=1:2;
else
   monkeyID=2; 
   selcell={'F:\Yami\V1_grating_3std.mat'};
%  selcell={'F:\Yami\V1_grating_45135.mat'};
   repeatday=8;%%always full when mstd==0
useday=[1:4 6:9];
end
% selcell={'F:\COCO\V1grating_3std.mat'};
% selcell={'F:\Yami\V1_grating_3std.mat'}; cl
trialssel=1; %%是否挑选trial
mstd=1;%%1==std other==xy+ori
% selcell={'F:\COCO\V1grating_3std.mat'};  

elecID=[];
showcell=0; %是否看单细胞
cutbase=4; %标准化  0不去基线  1去基线  4不标准化
% xylist={xy6;xy7;xy6;xy1;xy6;xy1;xy7;xy6;xy1;xy7;xy7;xy1;xy6;xy7};
% anglelist={p6;p7;p6;p1;p6;p1;p7;p6;p1;p7;p7;p1;p6;p7};

% xylist={xy6;xy6;xy7;xy1;xy7;xy6;xy1;xy7;xy7};
% anglelist={p6;p6;p7;p1;p7;p6;p1;p7;p7};
 dV1ori=[];
 dV1FixneuTTC=[];
 dV1FCneuTTCa=[];
 dV1FixpuffTTC=[];
 dV1FCpuffTTCa=[];
 
 dV1FCneuTTCb=[];
 dV1FCpuffTTCb=[];
 
  dV1FCneuTTCc=[];
 dV1FCpuffTTCc=[];
 dupFCneuTrial=[]; 
    dupFCpuffTrial=[];
    dupFixneuTrial=[];
      dupFixpuffTrial=[];
  dV1FCneuTTCd=[];
 dV1FCpuffTTCd=[];
dbot=0;
 bin=0.001;
 smoothlength=(0.01/bin)*2;

 
 load(['F:\COCO' '\ coco45halflessidx.mat']);
 load(['F:\COCO' '\ coco45halfmoreidx.mat']);
 load(['F:\COCO' '\ coco135halflessidx.mat']);
 load(['F:\COCO' '\ coco135halfmoreidx.mat']);
 load(['F:\YAMI' '\ yami45halfmoreidx.mat']);
 load(['F:\YAMI' '\ yami45halflessidx.mat']);
 load(['F:\YAMI' '\ yami135halfmoreidx.mat']);
 load(['F:\YAMI' '\ yami135halflessidx.mat']);
 
 for iday=1:numel(folderlist)
    iday
   upFCneuTrial=[]; 
    upFCpuffTrial=[];
     upFixneuTrial=[];
      upFixpuffTrial=[];
pFixpuffTrial=[];
pFixneuTrial=[];

pFCpuffTrial=[];
pFCneuTrial=[];
bot=[];
bot1=[];
bot2=[];
bot3=[];
bot4=[];

FCQ1=[];
FCQ2=[];
FCNQ1=[];
FCNQ2=[];
    
   FChitYa=[];
  FCcrXa=[];  
   FChitXa=[];
  FCcrYa=[];  
  
    FChitYb=[];
  FCcrXb=[];  
   FChitXb=[];
  FCcrYb=[];  
  
    FChitYc=[];
  FCcrXc=[];  
    FChitXc=[];
  FCcrYc=[];  
  
    FChitYd=[];
  FCcrXd=[];  
    FChitXd=[];
  FCcrYd=[]; 
    
  FCmissX=[];
  FCmissY=[];
  FChitX=[];
  FChitY=[];
  FCcrX=[];
  FCcrY=[];
  FCfaX=[];
  FCfaY=[];
  FCQ1=[];
  FCQ2=[];
  FixmissX=[];
  FixmissY=[];
  FixhitX=[];
  FixhitY=[];
  FixcrX=[];
  FixcrY=[];
  FixfaX=[];
  FixfaY=[];
  FixnsYa=[];
  FixnsXa=[];
  FixcsYa=[];
  FixcsXa=[];
  
  V1FCpuffTTC3b=[];
 V1FCneuTTC3b=[];%mean(V1FCneuTTC2b(:,:,1:bot),3);
%   V1FCpuffTTC3c=mean(V1FCpuffTTC2c,3);
%  V1FCneuTTC3c=mean(V1FCneuTTC2c,3);
%   V1FCpuffTTC3d=mean(V1FCpuffTTC2d,3);
%  V1FCneuTTC3d=mean(V1FCneuTTC2d,3);
 V1FixpuffTTC3=[];
 V1FixneuTTC3=[];    
%     FCpuffTso=[];
%     FCdifTso=[];
%     FCneuTso=[];
%     FixpuffTso=[];
%     FixdifTso=[];
%     FixneuTso=[];
%     FCuseblock=[];
%     Fixuseblock=[];
%      Fix2puffTso=[];
%     Fix2difTso=[];
%     Fix2neuTso=[];

%      load([folderlist{iday} '\Fix1difTso.mat'])
%      load([folderlist{iday} '\FCdifTso.mat'])
%         load([folderlist{iday} '\Fix1neuTso.mat'])
%      load([folderlist{iday} '\FCneuTso.mat'])
%          load([folderlist{iday} '\Fix1puffTso.mat'])
%      load([folderlist{iday} '\FCpuffTso.mat'])

%      load([folderlist{iday} '\Fix2difTso.mat'])
     
%         load([folderlist{iday} '\Fix2neuTso.mat'])
%      
%          load([folderlist{iday} '\Fix2puffTso.mat'])
    %%是否选trials
    
    if trialssel==1
       load([folderlist{iday} '\FCneuTrial.mat'])
       load([folderlist{iday} '\FCpuffTrial.mat'])
   
       
        load([folderlist{iday} '\pFCneuTrialx.mat'])
       load([folderlist{iday} '\pFCpuffTrialx.mat'])
       
        load([folderlist{iday} '\pFixneuTrialx.mat'])
       load([folderlist{iday} '\pFixpuffTrialx.mat'])
     
       
        load([folderlist{iday} '\lFCneuTrialx.mat'])
       load([folderlist{iday} '\lFCpuffTrialx.mat'])
       
             load([folderlist{iday} '\LAirFCneuTrialALLx.mat'])
       load([folderlist{iday} '\LAirFCpuffTrialALLx.mat'])
       
                 load([folderlist{iday} '\LAirFixneuTrialALLx.mat'])
       load([folderlist{iday} '\LAirFixpuffTrialALLx.mat'])
      
         load([folderlist{iday} '\LAirFixdifTsoALLx.mat'])
          load([folderlist{iday} '\LAirFCdifTsoALLx.mat'])
          
            load([folderlist{iday} '\LStiFixdifTsoALL.mat'])
          load([folderlist{iday} '\LStiFCdifTsoALL.mat'])
          
             load([folderlist{iday} '\LStiFixpuffTsoALL.mat'])
          load([folderlist{iday} '\LStiFCpuffTsoALL.mat'])
          
               load([folderlist{iday} '\LStiFixneuTsoALL.mat'])
          load([folderlist{iday} '\LStiFCneuTsoALL.mat'])
          
         load([folderlist{iday} '\LAirFixpuffTsoALL.mat'])
          load([folderlist{iday} '\LAirFCpuffTsoALL.mat'])
          
          
         load([folderlist{iday} '\LAirFixneuTsoALL.mat'])
          load([folderlist{iday} '\LAirFCneuTsoALL.mat'])
 
%               load([folderlist{iday} '\L35FixpuffTrialALL.mat'])
%           load([folderlist{iday} '\L35FCpuffTrialALL.mat'])
%           
%           
%          load([folderlist{iday} '\L35FixneuTrialALL.mat'])
%           load([folderlist{iday} '\L35FCneuTrialALL.mat'])
          
                   load([folderlist{iday} '\L35FixdifTsoALL.mat'])
          load([folderlist{iday} '\L35FCdifTsoALL.mat'])
          
          load([folderlist{iday} '\L35FixpuffTsoALL.mat'])
          load([folderlist{iday} '\L35FCpuffTsoALL.mat'])
           load([folderlist{iday} '\L35FixneuTsoALL.mat'])
          load([folderlist{iday} '\L35FCneuTsoALL.mat'])
          if mmon==1
               load([folderlist{iday} '\LAirFCneuTrialALL.mat'])
       load([folderlist{iday} '\LAirFCpuffTrialALL3.mat'])
       
                 load([folderlist{iday} '\LAirFixneuTrialALL.mat'])
       load([folderlist{iday} '\LAirFixpuffTrialALL.mat'])
          end
%    rFixpuffTrial=reshape(FixpuffTrial,1,[])';
%      [Fixpuffsafeidx,~]=find( rFixpuffTrial==0);
%        [Fixpuffdangeridx,~]=find( rFixpuffTrial>prctile(rFixpuffTrial,10));

if mmon==2
    
end

%  FCQ1=quantile(lFCpuffTrial(lFCpuffTrial~=10000),0.25);
%    FCQ2=quantile(lFCpuffTrial(lFCpuffTrial~=10000),0.5);
%    FCQ3=quantile(lFCpuffTrial(lFCpuffTrial~=10000),0.75);
    end
%%%   

aaa=LAirFixpuffTso(~(LAirFixpuffTso == 1 | LAirFixpuffTso== 2));
bbb=LAirFCpuffTso(~(LAirFCpuffTso == 100 | LAirFCpuffTso== 100));

 fcb=ceil(length(LAirFCpuffTso)/4);
if mmon==1
    fixb=ceil(length((LAirFixpuffTso))/3);
useFixblock=[LAirFixpuffTso(1:end)];%[LAirFixpuffTso(3:8)];LAirFixpuffTso(1:3)  LStiFixpuffTso(1:3)  LAirFixpuffTso(1:3)
else
        fixb=ceil((length(LAirFixpuffTso)-2)/3);
       useFixblock=[aaa(1:end)]; 
    end
%[LAirFixpuffTso(3:8)];LAirFixpuffTso(1:3)  LStiFixpuffTso(1:3)  LAirFixpuffTso(1:3)
% useFixblock=[LAirFixpuffTso(2:3)];
useFCblock=[bbb([1:end])];%[LAirFCdifTso([1:10])];%%要用的block LAirFCpuffTso([1:3LAirFCpuffTso(end-1:end)]) LAirFCpuffTso(end-1:end)

% pFCpuffTrial=pFCffTrial();
% pFCneuTrial=pFCneuTrial;
pFixpuffTrial=pFixpuffTrial(:,useFixblock);
pFixneuTrial=pFixneuTrial(1:20,useFixblock);

pFCpuffTrial=pFCpuffTrial(:,useFCblock);
pFCneuTrial=pFCneuTrial(1:20,useFCblock);

LAirFixpuffTrial=LAirFixpuffTrial(:,useFixblock);
LAirFixneuTrial=LAirFixneuTrial(1:20,useFixblock);
LAirFCpuffTrial=LAirFCpuffTrial(:,useFCblock);
LAirFCneuTrial=LAirFCneuTrial(1:20,useFCblock);

% LAirFixpuffTrial=LAirFixpuffTrial(:,useFixblock);
% LAirFixneuTrial=LAirFixneuTrial(1:20,useFixblock);
% LAirFCpuffTrial=LAirFCpuffTrial(:,useFCblock);
% LAirFCneuTrial=LAirFCneuTrial(1:20,useFCblock);


% 
%    %%%所有block的眨眼情况汇总，后面不会用到
for i=1:numel(useFCblock)
    mpFCpuff(iday,i)=mean(pFCpuffTrial(find(pFCpuffTrial(:,i)~=10000),i));
    stdpFCpuff(iday,i)=std(pFCpuffTrial(find(pFCpuffTrial(:,i)~=10000),i));
    mpFCneu(iday,i)=mean(pFCneuTrial(find(pFCneuTrial(:,i)~=10000),i));
    stdpFCneu(iday,i)=std(pFCneuTrial(find(pFCneuTrial(:,i)~=10000),i));
end

%  FCQ1=quantile(pFCpuffTrial(pFCpuffTrial~=10000),0.25);
%    FCQ2=quantile(pFCpuffTrial(pFCpuffTrial~=10000),0.5);
%    FCQ3=quantile(pFCpuffTrial(pFCpuffTrial~=10000),0.75);

%%计算每一天每个blcok的眨眼比例三等分点
   for j=1:numel(useFCblock)
%        aa(:,j)= pFCpuffTrial(:,j)~=10000;
%        FCQ1(j)=quantile(pFCpuffTrial(find(aa(:,j)==1),j),0.33);
%        FCQ2(j)=quantile(pFCpuffTrial(find(aa(:,j)==1),j),0.66);
       aa(:,j)= LAirFCpuffTrial(:,j)<=10000;
       FCQ1(j)=quantile(LAirFCpuffTrial(:,j),0.33);
       FCQ2(j)=quantile(LAirFCpuffTrial(:,j),0.66);
   end
  FCQA1=quantile(LAirFCpuffTrial(LAirFCpuffTrial<10000),0.33);
   FCQA2=quantile(LAirFCpuffTrial(LAirFCpuffTrial<10000),0.66);
   FCQA3=quantile(LAirFCpuffTrial(LAirFCpuffTrial<10000),0.8);

%       for j=1:numel(useFCblock)
%        dd(:,j)= pFCneuTrial(:,j)~=10000;
%        FCNQ1(j)=quantile(pFCneuTrial(find(dd(:,j)==1),j),0.66);
%        FCNQ2(j)=quantile(pFCneuTrial(find(dd(:,j)==1),j),0.66);
%       end
   
         for j=1:numel(useFixblock)
%        aa(:,j)= pFCpuffTrial(:,j)~=10000;
%        FCQ1(j)=quantile(pFCpuffTrial(find(aa(:,j)==1),j),0.33);
%        FCQ2(j)=quantile(pFCpuffTrial(find(aa(:,j)==1),j),0.66);
       FixQ1(j)=quantile(LAirFixpuffTrial(:,j),0.33);
       FixQ2(j)=quantile(LAirFixpuffTrial(:,j),0.66);
   end
      FixQA1=quantile(LAirFixpuffTrial(LAirFixpuffTrial<10000),0.33);
      FixQA2=quantile(LAirFixpuffTrial(LAirFixpuffTrial<10000),0.66);
      FixQA3=quantile(LAirFixpuffTrial(LAirFixpuffTrial<10000),0.8);
     xpFC=pFCpuffTrial;
  xpFC(find(xpFC==10000))=-2;
% 
% [sxpfc, indices] = sort(xpFC, 2, 'descend'); % 对每一列进行降序排序
[maxpFC, firstIndices] = max(xpFC, [], 1); % 找到每一列第二大值的索引
for i=1:numel(firstIndices)
xpFC(firstIndices,i)=-2;
end
[maxpFC2, firstIndices2] = max(xpFC, [], 1);
       


%     FCQ1=quantile(pFCpuffTrial(pFCpuffTrial~=10000),0.33);
%    FCQ2=quantile(pFCpuffTrial(pFCpuffTrial~=10000),0.66);
   
%    FCQ3=quantile(pFCpuffTrial(pFCpuffTrial~=10000),0.75);
   
%    FCQ1=quantile(pFCneuTrial(pFCneuTrial~=10000),0.25);
%    FCQ2=quantile(pFCneuTrial(pFCneuTrial~=10000),0.5);
%    FCQ3=quantile(pFCneuTrial(pFCneuTrial~=10000),0.75);
   
%    
%    
%    FixQ1=quantile(reshape(FixpuffTrial,1,[]),0.25);
%    FixQ2=quantile(reshape(FixpuffTrial,1,[]),0.5);
%    FixQ3=quantile(reshape(FixpuffTrial,1,[]),0.75);

% %%找到符合标准的trial的坐标   对CS
for j=1:numel(useFCblock)
%       [FCmissX,FCmissY]=find(pFCpuffTrial>0.5 & pFCpuffTrial<0.8);% & pFCpuffTrial~=10000
%       [FChitXa,FChitYa]=find(pFCpuffTrial<=FCQ1 & pFCpuffTrial~=10000);
%       [FCcrXa,FCcrYa]=find(pFCneuTrial<=0 & pFCneuTrial~=10000);
%       [FCfaX,FCfaY]=find(pFCneuTrial>-2 & pFCneuTrial~=10000);

  [tFChitXa,tFChitYa]=find(pFCpuffTrial(:,j)<=5000000  & pFCpuffTrial(:,j)~=100000 & pFCpuffTrial(:,j)~=maxpFC(j));  %%& pFCpuffTrial<=FCQ2 & pFCpuffTrial(:,j)~=maxpFC(j) & pFCpuffTrial(:,j)~=maxpFC2(j)
      tFChitYa=tFChitYa+j-1;  %y为blcok
      FChitXa=[FChitXa;tFChitXa];
      FChitYa=[FChitYa;tFChitYa]; 
      
      
%       [FCmissX,FCmissY]=find(pFCpuffTrial>0.5 & pFCpuffTrial<0.8);% & pFCpuffTrial~=10000
      [tFChitXb,tFChitYb]=find(LAirFCpuffTrial(:,j)>=0& LAirFCpuffTrial(:,j)<10000 );  %%& pFCpuffTrial<=FCQ2  & pFCpuffTrial(:,j)~=maxpFC(j)& pFCpuffTrial(:,j)~=10000 
      tFChitYb=tFChitYb+j-1;
      FChitXb=[FChitXb;tFChitXb];
      FChitYb=[FChitYb;tFChitYb];
      
%        [tFChitXb,tFChitYb]=find(LAirFCpuffTrial(:,j)>=0);  %%& pFCpuffTrial<=FCQ2  & pFCpuffTrial(:,j)~=maxpFC(j)
%       tFChitYb=tFChitYb+j-1;
%       FChitXb=[FChitXb;tFChitXb];
%       FChitYb=[FChitYb;tFChitYb];
      
      
      [tFChitXc,tFChitYc]=find(pFCpuffTrial(:,j)<=FCQ1(j)  );  %%& pFCpuffTrial<=FCQ2
      tFChitYc=tFChitYc+j-1;
      FChitXc=[FChitXc;tFChitXc];
      FChitYc=[FChitYc;tFChitYc];
      
      %%%%%%% 找到符合标准的trial的坐标   对NS  本代码后面没有使用
          [tFCcrXa,tFCcrYa]=find(pFCneuTrial(:,j)<=400000  & pFCneuTrial(:,j)~=10000);  %%& pFCneuTrial<=FCQ2
      tFCcrYa=tFCcrYa+j-1;
      FCcrXa=[FCcrXa;tFCcrXa];
      FCcrYa=[FCcrYa;tFCcrYa];
      
      
%       [FCmissX,FCmissY]=find(pFCneuTrial>0.5 & pFCneuTrial<0.8);% & pFCneuTrial~=10000
      [tFCcrXb,tFCcrYb]=find(LAirFCneuTrial(:,j)>=0 & LAirFCneuTrial(:,j)<10000 );  %%& pFCneuTrial<=FCQ2 & pFCneuTrial(:,j)~=10000 
      tFCcrYb=tFCcrYb+j-1;
      FCcrXb=[FCcrXb;tFCcrXb];
      FCcrYb=[FCcrYb;tFCcrYb];
%       
%        [tFCcrXb,tFCcrYb]=find(LAirFCneuTrial(:,j)>=0 );  %%& pFCneuTrial<=FCQ2
%       tFCcrYb=tFCcrYb+j-1;
%       FCcrXb=[FCcrXb;tFCcrXb];
%       FCcrYb=[FCcrYb;tFCcrYb];
      
      [tFCcrXc,tFCcrYc]=find(pFCneuTrial(:,j)==0 );  %%& pFCneuTrial<=FCQ2
      tFCcrYc=tFCcrYc+j-1;
      FCcrXc=[FCcrXc;tFCcrXc];
      FCcrYc=[FCcrYc;tFCcrYc];
      
end
for j=1:numel(useFixblock)
     [tFixnsXa,tFixnsYa]=find(LAirFixneuTrial(:,j)>=0 & LAirFixneuTrial(:,j)<10000 );  %%& pFCneuTrial<=FCQ2  & pFixneuTrial(:,j)~=10000
      tFixnsYa=tFixnsYa+j-1;
      FixnsXa=[FixnsXa;tFixnsXa];
      FixnsYa=[FixnsYa;tFixnsYa];
      
     [tFixcsXa,tFixcsYa]=find(LAirFixpuffTrial(:,j)>=0& LAirFixpuffTrial(:,j)<10000 );  %%& pFCneuTrial<=FCQ2 & pFixpuffTrial(:,j)~=10000 
      tFixcsYa=tFixcsYa+j-1;
      FixcsXa=[FixcsXa;tFixcsXa];
      FixcsYa=[FixcsYa;tFixcsYa];
    
%         [tFixnsXa,tFixnsYa]=find(LAirFixneuTrial(:,j)>=0  );  %%& pFCneuTrial<=FCQ2
%       tFixnsYa=tFixnsYa+j-1;
%       FixnsXa=[FixnsXa;tFixnsXa];
%       FixnsYa=[FixnsYa;tFixnsYa];
%       
%      [tFixcsXa,tFixcsYa]=find(LAirFixpuffTrial(:,j)>=0  );  %%& pFCneuTrial<=FCQ2
%       tFixcsYa=tFixcsYa+j-1;
%       FixcsXa=[FixcsXa;tFixcsXa];
%       FixcsYa=[FixcsYa;tFixcsYa];
    
end



%       [FCcrXb,FCcrYb]=find(pFCneuTrial<=0 & pFCneuTrial~=10000);
      
%        [FChitXc,FChitYc]=find(pFCpuffTrial>FCQ2  & pFCpuffTrial~=10000); %%& pFCpuffTrial<=FCQ3
%       [FCcrXc,FCcrYc]=find(pFCneuTrial>-2  & pFCneuTrial~=10000);
      
%        [FChitXd,FChitYd]=find(pFCpuffTrial>FCQ3  & pFCpuffTrial~=10000);
%       [FCcrXd,FCcrYd]=find(pFCneuTrial>0 & pFCneuTrial~=10000);
%       [FCfaX,FCfaY]=find(pFCneuTrial>-2 & pFCneuTrial~=10000);
            
%          [FixmissX,FixmissY]=find(pFixpuffTrial>-2 & pFixpuffTrial~=10000);
%         [FixhitX,FixhitY]=find(pFixpuffTrial>-2 & pFixpuffTrial~=10000);
%           [FixcrX,FixcrY]=find(pFixneuTrial>-2 & pFixneuTrial~=10000);
%             [FixfaX,FixfaY]=find(pFixneuTrial>-2 & pFixneuTrial~=10000);
            
%         rFixneuTrial=reshape(FixneuTrial,1,[])';
%      [Fixneusafeidx,~]=find( rFixneuTrial<20);
%        [Fixneudangeridx,~]=find( rFixneuTrial~=0);
%        
%            rFCneuTrial=reshape(FCneuTrial,1,[])';
%      [FCneuCRidx,~]=find( rFCneuTrial==0);
%        [FCneudangeridx,~]=find( rFCneuTrial>prctile(rFCneuTrial,50));
%        
%          rFCpuffTrial=reshape(FCpuffTrial,1,[])';
%      [FCpuffmissidx,~]=find( rFCpuffTrial>=0 & rFCpuffTrial<800);
%        [FCpuffhitidx,~]=find( rFCpuffTrial>50&rFCpuffTrial<900);


   
         
%    FixneuTso( find((FixneuTso<5)))=[];
%    FixpuffTso( find((FixpuffTso<5)))=[];
%    FixdifTso( find((FixdifTso<5)))=[];
   
%    FixneuTso( find((FixneuTso<6)))=[];
%    FixpuffTso( find((FixpuffTso<6)))=[];
%    FixdifTso( find((FixdifTso<6)))=[];

%  FCuseblock=[FCdifTso(end-4:end)];
% Fixuseblock=[ FixdifTso(1:5) ];

 FCuseblock=[useFCblock];%[FCpuffTso(end-6:end)];%[FCneuTso(1:10)];
Fixuseblock=[useFixblock];%[FixpuffTso(end-1:end)];

% if iday==1 || iday==2 ||iday==6
%      Fixuseblock=[1:8];
% end
% 
% if iday==2
%     FCuseblock=[1:7];
% end
% if iday>2
%     FCuseblock=[1:8];
% end
% if iday==3%| iday==4
%      Fixuseblock=[1:7];
% end
% 
% if iday>=4
%      Fixuseblock=[1:8];
% end
% 
% if iday==5
%      FCuseblock=[1:12];
% end
% 
% if iday==6
%      FCuseblock=[1:13];
% end
%  FCuseblock=FCblocklist{iday};
% Fixuseblock=Fixblocklist{iday};
% oriOP=1;
FCfrth=0.002;
bFCfrth=1000;
Fixfrth=0.002;
%  FCuseblock=[FCneuTso(1:4)];
% Fixuseblock=[ FixneuTso(1:4) ];

 Fixusetrials=numel(Fixuseblock)*10;
 FCusetrials=numel(FCuseblock)*10;
 
V1FCpsth=[];
V1Fixpsth=[];
nearidx=[];
 optimidx=[];
 ootimidx=[];
 V1FixneuTTC=[];
 V1FCneuTTC=[];
 V1FixpuffTTC=[];
V1FCpuffTTC=[];
 V1FixneuTTC2=[];
 V1FCneuTTC2=[];
 V1FixpuffTTC2=[];
V1FCpuffTTC2=[];
 V1FixneuTTC3=[];
 V1FCneuTTC3=[];
 V1FixpuffTTC3=[];
V1FCpuffTTC3=[];


 V1FCneuTTC2a=[];
V1FCpuffTTC2a=[];
 V1FCneuTTC3a=[];
V1FCpuffTTC3a=[];

 V1FCneuTTC2b=[];
V1FCpuffTTC2b=[];
 V1FCneuTTC3b=[];
V1FCpuffTTC3b=[];

 V1FCneuTTC2c=[];
V1FCpuffTTC2c=[];
 V1FCneuTTC3c=[];
V1FCpuffTTC3c=[];

 V1FCneuTTC2d=[];
V1FCpuffTTC2d=[];
 V1FCneuTTC3d=[];
V1FCpuffTTC3d=[];

useori={};
if mstd==1
    select='xy';
else
select='both';
end


if monkeyID==1

cmppath = 'F:\COCO\SN 4566-0905.cmp';

cmpinfo=LoadCmp(cmppath,1,0);
elec=cmpinfo{1,1}.RealElec(:,6:10);
else 
cmppath = 'E:\file\240524 Yami array\SN 4566-004425.cmp';

cmpinfo=LoadCmp(cmppath,1,0);
elec=cmpinfo{1,1}.RealElec(11:18,:);
end
 
%      load([folderlist{iday} '\V1Taskblockunitpsth.mat']) 
if mstd==1
      load([folderlist{iday} '\V1Fixblockunitpsthxy.mat'])
    load([folderlist{iday} '\V1FCblockunitpsthxy.mat'])
else
    load([folderlist{iday} '\V1Fixblockunitpsth.mat'])
    load([folderlist{iday} '\V1FCblockunitpsth.mat'])
end
     load([folderlist{iday} '\V1XYvalid.mat'])

      load([selcell{1}])   

    load([folderlist{iday} '\V1orivalid.mat'])   
    load([folderlist{iday} '\V1xtun.mat'])
    load([folderlist{iday} '\V1ytun.mat'])   
    load([folderlist{iday} '\V1oritun.mat'])   
    
    selecti=lower(select);
switch selecti
    case 'xy'

    valididx=V1XYvalid;
    case 'ori'
        valididx=V1orivalid;
    case 'both'
        valididx=V1orivalid & V1XYvalid;
    case 'all'
        valididx=ones(12,8);
    otherwise
        msgbox('wrong select idx')
end
    validelec=elec(valididx);
    
    %%未使用
    V1ori=oparamV1{1,1}{1,4}(valididx);
    V1orisd=oparamV1{1,1}{1,5}(valididx);
%     iA = ~isnan(V1ori);
%     V1ori =  V1ori(iA(:));
    V1ori=round(V1ori,1);
    V1orisd=round(V1orisd,1);
    for k=1:size(validelec)
        if V1ori(k)>180
            V1ori(k)=V1ori(k)-180;
        elseif V1ori(k)<0 && V1ori(k)>=-180
            V1ori(k)=V1ori(k)+180;
        elseif V1ori(k)<-180 
            V1ori(k)=V1ori(k)+360;
        else
            V1ori(k)=V1ori(k);
        end
    end
            
    
    
     V1X=xparamV1{1,1}{1,4}(valididx);
%     iA = ~isnan(V1X);
%     V1X =  V1X(iA(:));
    V1X=round(V1X,1);
    
    V1Y=yparamV1{1,1}{1,4}(valididx);
%     iA = ~isnan(V1Y);
%     V1Y =  V1Y(iA(:));
    V1Y=round(V1Y,1);
    
    V1Rx=1.96*xparamV1{1, 1}{1, 5}(valididx);
%     iA = ~isnan(V1Rx);
    V1Rx =  round(V1Rx,1);
    V1rx=xparamV1{1, 1}{1, 5}(valididx);
    V1ry=yparamV1{1, 1}{1, 5}(valididx);
    V1Ry=1.96*yparamV1{1, 1}{1, 5}(valididx);
%     iA = ~isnan(V1Ry);
    V1Ry =  round(V1Ry,1);
   
%    V1FCpsth=V1FCblockunitpsth.psth(:,:,:,:,:);
%    V1Fixpsth=V1fixblockunitpsth.psth(:,:,:,:,:);
   %%%导入psth
       V1FCpsth=permute(V1FCblockunitpsth.psth,[1 4 5 2 3]);
       V1Fixpsth=permute(V1fixblockunitpsth.psth,[1 4 5 2 3]);
 %% position  
 
%  V1FCpuffTTC=reshape(squeeze(V1FCpsth(:,:,FCuseblock,1:2,:)),[800 20*numel(FCuseblock) size(V1FCblockunitpsth.psth,4)]);
%  V1FCneuTTC=reshape(squeeze(V1FCpsth(:,:,FCuseblock,3:6,:)),[800 40*numel(FCuseblock) size(V1FCblockunitpsth.psth,4)]);
%  V1FixpuffTTC=reshape(squeeze(V1Fixpsth(:,:,Fixuseblock,1:2,:)),[800 20*numel(Fixuseblock) size(V1fixblockunitpsth.psth,4)]);
%  V1FixneuTTC=reshape(squeeze(V1Fixpsth(:,:,Fixuseblock,3:6,:)),[800 40*numel(Fixuseblock) size(V1fixblockunitpsth.psth,4)]);
 
%%确保psth和行为数据保持一致，重点检查
  V1FCpuffTTC=reshape(squeeze(V1FCpsth(:,:,FCuseblock,:,1:2)),[600 size(V1FCblockunitpsth.psth,4) numel(FCuseblock) 20]);%%确保psth和行为数据保持一致，重点检查
 V1FCneuTTC=reshape(squeeze(V1FCpsth(:,:,FCuseblock,:,3:4)),[600  size(V1FCblockunitpsth.psth,4)  numel(FCuseblock) 20]);
 V1FixpuffTTC=reshape(squeeze(V1Fixpsth(:,:,Fixuseblock,:,1:2)),[600  size(V1fixblockunitpsth.psth,4) numel(Fixuseblock) 20]);
 V1FixneuTTC=reshape(squeeze(V1Fixpsth(:,:,Fixuseblock,:,3:4)),[600  size(V1fixblockunitpsth.psth,4) numel(Fixuseblock) 20]);
   

%  V1FixpuffTTC=reshape(squeeze(V1Fixpsth(:,:,Fixuseblock,1:2,:)),[600 20 numel(Fixuseblock) size(V1fixblockunitpsth.psth,4)]);
%  V1FixneuTTC=reshape(squeeze(V1Fixpsth(:,:,Fixuseblock,3:6,:)),[600 40 numel(Fixuseblock) size(V1fixblockunitpsth.psth,4)]);
   V1FCpuffTTC=permute(V1FCpuffTTC,[1 4 3 2]);
   V1FCneuTTC=permute(V1FCneuTTC,[1 4 3 2]);
   
    V1FixpuffTTC=permute(V1FixpuffTTC,[1 4 3 2]);
   V1FixneuTTC=permute(V1FixneuTTC,[1 4 3 2]);



%    V1FCpuffTTC=V1FCpuffTTC(:,FCpuffmissidx(1:50),:);
%   V1FCneuTTC=V1FCneuTTC(:,FCneuCRidx(1:50),:);
%   V1FixpuffTTC=V1FixpuffTTC(:,Fixpuffsafeidx(1:50),:);
%   V1FixneuTTC=V1FixneuTTC(:,safeidx(1:50),:);

%%三等分分别导出为a，b，c。  d导出但没有使用，只是为了方便以后添加条件
%  for i=1:numel(FChitXa)
%      V1FCpuffTTC2a(:,:,i)=squeeze(V1FCpuffTTC(:,FChitXa(i),FChitYa(i),:));
%  end
 
 for i=1:numel(FChitXb)
     V1FCpuffTTC2b(:,:,i)=squeeze(V1FCpuffTTC(:,FChitXb(i),FChitYb(i),:));
     upFCpuffTrial(i)=pFCpuffTrial(FChitXb(i),FChitYb(i));

     
 end
 
 
%   for i=1:numel(FChitXc)
%      V1FCpuffTTC2c(:,:,i)=squeeze(V1FCpuffTTC(:,FChitXc(i),FChitYc(i),:));
%   end
%  
%     for i=1:numel(FChitXd)
%      V1FCpuffTTC2d(:,:,i)=squeeze(V1FCpuffTTC(:,FChitXd(i),FChitYd(i),:));
%  end
     
 
%   for i=1:numel(FCcrXa)
%      V1FCneuTTC2a(:,:,i)=squeeze(V1FCneuTTC(:,FCcrXa(i),FCcrYa(i),:));
%   end
  
  
   for i=1:numel(FCcrXb)
     V1FCneuTTC2b(:,:,i)=squeeze(V1FCneuTTC(:,FCcrXb(i),FCcrYb(i),:));
      upFCneuTrial(i)=pFCneuTrial(FCcrXb(i),FCcrYb(i));
   end
  
   
   
   for i=1:numel(FixnsXa)
     V1FixneuTTC2(:,:,i)=squeeze(V1FixneuTTC(:,FixnsXa(i),FixnsYa(i),:));
     upFixneuTrial(i)=pFixneuTrial(FixnsXa(i),FixnsYa(i));
   end
   
   for i=1:numel(FixcsXa)
     V1FixpuffTTC2(:,:,i)=squeeze(V1FixpuffTTC(:,FixcsXa(i),FixcsYa(i),:));
     upFixpuffTrial(i)=pFixpuffTrial(FixcsXa(i),FixcsYa(i));
   end
%      for i=1:numel(FCcrXc)
%      V1FCneuTTC2c(:,:,i)=squeeze(V1FCneuTTC(:,FCcrXc(i),FCcrYc(i),:));
%      end
% 
%      for i=1:numel(FCcrXd)
%      V1FCneuTTC2d(:,:,i)=squeeze(V1FCneuTTC(:,FCcrXd(i),FCcrYd(i),:));
%      end


%    for i=1:numel(FCcrXb)
%      V1FCneuTTC2(:,:,i)=squeeze(V1FCneuTTC(:,FCcrXb(i),FCcrYb(i),:));
%    end
 
%    for i=1:numel(FixmissX)
%      V1FixpuffTTC2(:,:,i)=squeeze(V1FixpuffTTC(:,FixmissX(i),FixmissY(i),:));
%    end
%  
%     for i=1:numel(FixcrX)
%      V1FixneuTTC2(:,:,i)=squeeze(V1FixneuTTC(:,FixcrX(i),FixcrY(i),:));
%  end
 [~,~,bot1]=size(V1FCpuffTTC2b);
  [~,~,bot2]=size(V1FCneuTTC2b);
   [~,~,bot3]=size(V1FixpuffTTC2);
    [~,~,bot4]=size(V1FixneuTTC2);
  if min([bot1 bot2 bot3 bot4])==bot1
      bot=bot1;
  elseif min([bot1 bot2 bot3 bot4])==bot2
      bot=bot2;
  elseif min([bot1 bot2 bot3 bot4])==bot3
      bot=bot3;
  else
        bot=bot4;
  end
  if min([bot1 bot2])==bot1
  bota=bot1;
  else
      bota=bot2;
  end
  
   if min([bot3 bot4])==bot3
  botb=bot3;
  else
      botb=bot4;
  end
%   rng(0);
%   r1 = randperm(bot1, bot);
%     r2 = randperm(bot2, bot);
%       r3 = randperm(bot3, bot);
%        r4 = randperm(bot4, bot);

 dbot=dbot+bot; 
%  V1FCpuffTTC3a=mean(V1FCpuffTTC2a,3);
%  V1FCneuTTC3a=mean(V1FCneuTTC2a,3);

%   V1FCpuffTTC3b=mean(V1FCpuffTTC2b(:,:,r1),3);
%  V1FCneuTTC3b=mean(V1FCneuTTC2b(:,:,r2),3);%mean(V1FCneuTTC2b(:,:,1:end),3);
% 
%  V1FixpuffTTC3=mean(V1FixpuffTTC2(:,:,r3),3);
%  V1FixneuTTC3=mean(V1FixneuTTC2(:,:,r4),3);
% 
%   V1FCpuffTTC3b=mean(V1FCpuffTTC2b(:,:,1:end),3);
%  V1FCneuTTC3b=mean(V1FCneuTTC2b(:,:,1:end),3);%mean(V1FCneuTTC2b(:,:,1:end),3);
% 
%  V1FixpuffTTC3=mean(V1FixpuffTTC2(:,:,1:end),3);
%  V1FixneuTTC3=mean(V1FixneuTTC2(:,:,1:end),3);
%%

 if mmon==1
%   V1FCpuffTTC3b=mean(V1FCpuffTTC2b(:,:,end-bot+1:end),3);
%  V1FCneuTTC3b=mean(V1FCneuTTC2b(:,:,end-bot+1:end),3);%mean(V1FCneuTTC2b(:,:,1:end),3);
% % 
%  V1FixpuffTTC3=mean(V1FixpuffTTC2(:,:,end-bot+1:end),3);
%  V1FixneuTTC3=mean(V1FixneuTTC2(:,:,end-bot+1:end),3);


  V1FCpuffTTC3b=mean(V1FCpuffTTC2b(:,:,1:bota),3);
 V1FCneuTTC3b=mean(V1FCneuTTC2b(:,:,1:bota),3);%mean(V1FCneuTTC2b(:,:,1:end),3);
% 
 V1FixpuffTTC3=mean(V1FixpuffTTC2(:,:,1:botb),3);
 V1FixneuTTC3=mean(V1FixneuTTC2(:,:,1:botb),3);
 else
     
      V1FCpuffTTC3b=mean(V1FCpuffTTC2b(:,:,1:bota),3);
 V1FCneuTTC3b=mean(V1FCneuTTC2b(:,:,1:bota),3);%mean(V1FCneuTTC2b(:,:,1:end),3);
% 
 V1FixpuffTTC3=mean(V1FixpuffTTC2(:,:,1:botb),3);
 V1FixneuTTC3=mean(V1FixneuTTC2(:,:,1:botb),3);
%        V1FCpuffTTC3b=mean(V1FCpuffTTC2b(:,:,1:bot),3);
%  V1FCneuTTC3b=mean(V1FCneuTTC2b(:,:,1:bot),3);%mean(V1FCneuTTC2b(:,:,1:end),3);
% 
%  V1FixpuffTTC3=mean(V1FixpuffTTC2(:,:,1:bot),3);
%  V1FixneuTTC3=mean(V1FixneuTTC2(:,:,1:bot),3);
 end
 %%
%  dupFCneuTrial=[]; 
    upFCpuffTrial=upFCpuffTrial(1:bot);
    upFCneuTrial=upFCneuTrial(1:bot);
    upFixneuTrial=upFixneuTrial(1:bot);
    upFixpuffTrial=upFixpuffTrial(1:bot);
  
%   V1FCpuffTTC3b=mean(V1FCpuffTTC2b(:,:,end-bot+1:end),3);
%  V1FCneuTTC3b=mean(V1FCneuTTC2b(:,:,end-bot+1:end),3);%mean(V1FCneuTTC2b(:,:,1:end),3);
% 
%  V1FixpuffTTC3=mean(V1FixpuffTTC2(:,:,end-bot+1:end),3);
%  V1FixneuTTC3=mean(V1FixneuTTC2(:,:,end-bot+1:end),3);
%  
% 
maxV1FCpuffTTC3b = max(filtfilt(ones(1,10)/10, 1, V1FCpuffTTC3b));
maxV1FCneuTTC3b = max(filtfilt(ones(1,10)/10, 1, V1FCneuTTC3b));
maxV1FixpuffTTC3 = max(filtfilt(ones(1,10)/10, 1, V1FixpuffTTC3));
maxV1FixneuTTC3 = max(filtfilt(ones(1,10)/10, 1, V1FixneuTTC3));

qmaxV1FCpuffTTC3b = max(filtfilt(ones(1,10)/10, 1, V1FCpuffTTC3b-repmat(mean(V1FCpuffTTC3b(norwin,:)),[size(V1FCpuffTTC3b,1),1])));
qmaxV1FCneuTTC3b = max(filtfilt(ones(1,10)/10, 1, V1FCneuTTC3b-repmat(mean(V1FCneuTTC3b(norwin,:)),[size(V1FCneuTTC3b,1),1])));
qmaxV1FixpuffTTC3 = max(filtfilt(ones(1,10)/10, 1, V1FixpuffTTC3-repmat(mean(V1FixpuffTTC3(norwin,:)),[size(V1FixpuffTTC3,1),1])));
qmaxV1FixneuTTC3 = max(filtfilt(ones(1,10)/10, 1, V1FixneuTTC3-repmat(mean(V1FixneuTTC3(norwin,:)),[size(V1FixneuTTC3,1),1])));


% V1FCpuffTTC3b = filtfilt(ones(1,10)/10, 1, V1FCpuffTTC3b-repmat(mean(V1FCpuffTTC3b(norwin,:)),[size(V1FCpuffTTC3b,1),1]));
% V1FCneuTTC3b = filtfilt(ones(1,10)/10, 1, V1FCneuTTC3b-repmat(mean(V1FCneuTTC3b(norwin,:)),[size(V1FCneuTTC3b,1),1]));
% V1FixpuffTTC3 = filtfilt(ones(1,10)/10, 1, V1FixpuffTTC3-repmat(mean(V1FixpuffTTC3(norwin,:)),[size(V1FixpuffTTC3,1),1]));
% V1FixneuTTC3 = filtfilt(ones(1,10)/10, 1, V1FixneuTTC3-repmat(mean(V1FixneuTTC3(norwin,:)),[size(V1FixneuTTC3,1),1]));
% 
% if norn==1
%      V1FCpuffTTC3b=V1FCpuffTTC3b./repmat(max(V1FCneuTTC3b),[size(V1FCpuffTTC3b,1),1]);
%  V1FCneuTTC3b=V1FCneuTTC3b./repmat(max(V1FCneuTTC3b),[size(V1FCneuTTC3b,1),1]);
% 
% V1FixpuffTTC3=V1FixpuffTTC3./repmat(max(V1FixneuTTC3),[size(V1FixpuffTTC3,1),1]);
% V1FixneuTTC3=V1FixneuTTC3./repmat(max(V1FixneuTTC3),[size(V1FixneuTTC3,1),1]);
%  end
%  if norn==2
%   V1FCneuTTC3b=(V1FCneuTTC3b-repmat(mean(V1FCneuTTC3b(norwin,:)),[size(V1FCneuTTC3b,1),1]))./repmat(max(V1FixneuTTC3),[size(V1FCneuTTC3b,1),1]);
%   V1FCpuffTTC3b=(V1FCpuffTTC3b-repmat(mean(V1FCpuffTTC3b(norwin,:)),[size(V1FCpuffTTC3b,1),1]))./repmat(max(V1FixneuTTC3),[size(V1FCpuffTTC3b,1),1]);
%   V1FixpuffTTC3=(V1FixpuffTTC3-repmat(mean(V1FixpuffTTC3(norwin,:)),[size(V1FixpuffTTC3,1),1]))./repmat(max(V1FixneuTTC3),[size(V1FixpuffTTC3,1),1]);
%   V1FixneuTTC3=(V1FixneuTTC3-repmat(mean(V1FixneuTTC3(norwin,:)),[size(V1FixneuTTC3,1),1]))./repmat(max(V1FixneuTTC3),[size(V1FixneuTTC3,1),1]);
%  
%  
%  end
%  
%   if norn==3
%  
%       
%       
%   V1FCpuffTTC3b=(V1FCpuffTTC3b-repmat(mean(V1FCpuffTTC3b(norwin,:)),[size(V1FCpuffTTC3b,1),1]))./repmat(max(V1FCneuTTC3b),[size(V1FCpuffTTC3b,1),1]);
%   V1FCneuTTC3b=(V1FCneuTTC3b-repmat(mean(V1FCneuTTC3b(norwin,:)),[size(V1FCneuTTC3b,1),1]))./repmat(max(V1FCneuTTC3b),[size(V1FCneuTTC3b,1),1]);
%    
%   V1FixpuffTTC3=(V1FixpuffTTC3-repmat(mean(V1FixpuffTTC3(norwin,:)),[size(V1FixpuffTTC3,1),1]))./repmat(max(V1FixneuTTC3),[size(V1FixpuffTTC3,1),1]);
%   V1FixneuTTC3=(V1FixneuTTC3-repmat(mean(V1FixneuTTC3(norwin,:)),[size(V1FixneuTTC3,1),1]))./repmat(max(V1FixneuTTC3),[size(V1FixneuTTC3,1),1]);
%  
%  
%  end


%       V1FCpuffTTC3b=convn(V1FCpuffTTC3b,ones(smoothlength,1),'same')/smoothlength;
%       V1FCneuTTC3b=convn(V1FCneuTTC3b,ones(smoothlength,1),'same')/smoothlength;
%       V1FixpuffTTC3=convn(V1FixpuffTTC3,ones(smoothlength,1),'same')/smoothlength;
%       V1FixneuTTC3=convn(V1FixneuTTC3,ones(smoothlength,1),'same')/smoothlength;

 if norn==1
     V1FCpuffTTC3b=V1FCpuffTTC3b./repmat(maxV1FCneuTTC3b,[size(V1FCpuffTTC3b,1),1]);
 V1FCneuTTC3b=V1FCneuTTC3b./repmat(maxV1FCneuTTC3b,[size(V1FCneuTTC3b,1),1]);

V1FixpuffTTC3=V1FixpuffTTC3./repmat(maxV1FixneuTTC3,[size(V1FixpuffTTC3,1),1]);
V1FixneuTTC3=V1FixneuTTC3./repmat(maxV1FixneuTTC3,[size(V1FixneuTTC3,1),1]);
 end
 if norn==2
  V1FCneuTTC3b=(V1FCneuTTC3b-repmat(mean(V1FCneuTTC3b(norwin,:)),[size(V1FCneuTTC3b,1),1]))./repmat(qmaxV1FixneuTTC3,[size(V1FCneuTTC3b,1),1]);
  V1FCpuffTTC3b=(V1FCpuffTTC3b-repmat(mean(V1FCpuffTTC3b(norwin,:)),[size(V1FCpuffTTC3b,1),1]))./repmat(qmaxV1FixneuTTC3,[size(V1FCpuffTTC3b,1),1]);
  V1FixpuffTTC3=(V1FixpuffTTC3-repmat(mean(V1FixpuffTTC3(norwin,:)),[size(V1FixpuffTTC3,1),1]))./repmat(qmaxV1FixneuTTC3,[size(V1FixpuffTTC3,1),1]);
  V1FixneuTTC3=(V1FixneuTTC3-repmat(mean(V1FixneuTTC3(norwin,:)),[size(V1FixneuTTC3,1),1]))./repmat(qmaxV1FixneuTTC3,[size(V1FixneuTTC3,1),1]);
 
 
 end
 
  if norn==3
 
      
      
  V1FCpuffTTC3b=(V1FCpuffTTC3b-repmat(mean(V1FCpuffTTC3b(norwin,:)),[size(V1FCpuffTTC3b,1),1]))./repmat(qmaxV1FCneuTTC3b,[size(V1FCpuffTTC3b,1),1]);
  V1FCneuTTC3b=(V1FCneuTTC3b-repmat(mean(V1FCneuTTC3b(norwin,:)),[size(V1FCneuTTC3b,1),1]))./repmat(qmaxV1FCneuTTC3b,[size(V1FCneuTTC3b,1),1]);
   
  V1FixpuffTTC3=(V1FixpuffTTC3-repmat(mean(V1FixpuffTTC3(norwin,:)),[size(V1FixpuffTTC3,1),1]))./repmat(qmaxV1FixneuTTC3,[size(V1FixpuffTTC3,1),1]);
  V1FixneuTTC3=(V1FixneuTTC3-repmat(mean(V1FixneuTTC3(norwin,:)),[size(V1FixneuTTC3,1),1]))./repmat(qmaxV1FixneuTTC3,[size(V1FixneuTTC3,1),1]);
 
 
 end
 elecID=[elecID;validelec];
      
      %%不同天整合
%    dV1FixneuTTC=cat(2,dV1FixneuTTC,V1FixneuTTC3);
%    dV1FCneuTTCa=cat(2,dV1FCneuTTCa,V1FCneuTTC3a);
%    dV1FCpuffTTCa=cat(2,dV1FCpuffTTCa,V1FCpuffTTC3a);
      dV1FCneuTTCb=cat(2,dV1FCneuTTCb,V1FCneuTTC3b);
   dV1FCpuffTTCb=cat(2,dV1FCpuffTTCb,V1FCpuffTTC3b);
%       dV1FCneuTTCc=cat(2,dV1FCneuTTCc,V1FCneuTTC3c);
%    dV1FCpuffTTCc=cat(2,dV1FCpuffTTCc,V1FCpuffTTC3c);
      dV1FixneuTTC=cat(2,dV1FixneuTTC,V1FixneuTTC3);
   dV1FixpuffTTC=cat(2,dV1FixpuffTTC,V1FixpuffTTC3);
   dV1ori=[dV1ori;V1ori];
   
   dupFCpuffTrial=[dupFCpuffTrial;upFCpuffTrial'];
    dupFCneuTrial=[dupFCneuTrial;upFCneuTrial'];
    dupFixneuTrial=[dupFixneuTrial;upFixneuTrial'];
    dupFixpuffTrial=[dupFixpuffTrial;upFixpuffTrial'];
   
 end
    mdupFCpuffTrial=mean(dupFCpuffTrial);
    mdupFCneuTrial=mean(dupFCneuTrial);
    mdupFixneuTrial=mean(dupFixneuTrial);
    mdupFixpuffTrial=mean(dupFixpuffTrial);
    
      stddupFCpuffTrial=std(dupFCpuffTrial);
    stddupFCneuTrial=std(dupFCneuTrial);
    stddupFixneuTrial=std(dupFixneuTrial);
    stddupFixpuffTrial=std(dupFixpuffTrial);
    %%%%%行为%%%%%
%     figure
%     x=1:4;
%     y=[ mdupFCpuffTrial mdupFCneuTrial  mdupFixpuffTrial mdupFixneuTrial];
%     error=[ stddupFCpuffTrial stddupFCneuTrial  stddupFixpuffTrial stddupFixneuTrial];
%     categories={'FC-CS (puff)', 'FC-NS', 'Fix-CS' ,'Fix-NS'};
%     bar(x, y); % 首先创建条形图
% hold on; % 保持当前图像
% for i = 1:length(x)
%     % 为每个条形添加误差条
%     % 注意：误差条的中心要与条形的中心对齐，所以使用x的位置，但y值需要调整以考虑条形的高度和误差
%     errorbar(x(i), y(i), error(i), 'v', 'MarkerEdgeColor','k'); % 'v' 表示垂直误差条，'k' 是黑色边缘
% end
% ylabel('BlinkTime Ratio');
% xticklabels(categories);
% set(gca,'fontsize',20);

%%%%%%%%%%%%%%%
 %%相同细胞归一
%  [uniqueValues, ~, idx] = unique(elecID,'stable');
% 
% counts = accumarray(idx, 1);
% selectedElements = uniqueValues(counts == 8);
selectedElements=[];
  NewelecID=cell2mat(cellname(useday));
 if mstd==1
 [uniqueValues, ~, idx] = unique(NewelecID,'stable');
 else
  [uniqueValues, ~, idx] = unique(elecID,'stable');
 end



counts = accumarray(idx, 1);
selectedElements = uniqueValues(counts >= repeatday);
% selectedElements=selectedElements(find(selectedElements~=[16]));
% selectedElements=selectedElements(find(selectedElements~=[11]));
% % selectedElements=selectedElements(find(selectedElements~=[30]));
% selectedElements=selectedElements(find(selectedElements~=[13]));
% selectedElements=selectedElements(find(selectedElements~=[117]));
% % selectedElements=selectedElements(find(selectedElements~=[106]));
% % selectedElements=selectedElements(find(selectedElements~=[108]));
% selectedElements=selectedElements(find(selectedElements~=[100]));
% selectedElements=selectedElements(find(selectedElements~=[6]));

if iday==10086
%    mdV1FixneuTTC=squeeze(mean(dV1FixneuTTC,2));
%    mdV1FCneuTTC=squeeze(mean(dV1FCneuTTC,2));
%    mdV1FixpuffTTC=squeeze(mean(dV1FixpuffTTC,2));
%    mdV1FCpuffTTC=squeeze(mean(dV1FCpuffTTC,2));
   
%   mdV1FixneuTTC=dV1FixneuTTC;
%    mdV1FCneuTTCa=dV1FCneuTTCa;
%    mdV1FCpuffTTCa=dV1FCpuffTTCa;
   mdV1FCneuTTCb=dV1FCneuTTCb;
   mdV1FCpuffTTCb=dV1FCpuffTTCb;
%    mdV1FCneuTTCc=dV1FCneuTTCc;
%    mdV1FCpuffTTCc=dV1FCpuffTTCc;
%    mdV1FCneuTTCd=dV1FCneuTTCd;
%    mdV1FCpuffTTCd=dV1FCpuffTTCd;
   mdV1FixneuTTC=dV1FixneuTTC;
   mdV1FixpuffTTC=dV1FixpuffTTC;
    mdV1ori=dV1ori';
else
      mmdV1FCneuTTCb=[];
      mmdV1FCpuffTTCb=[];
        mmdV1FixneuTTC=[];
   mmdV1FixpuffTTC=[];
%    for i=1:numel(uniqueValues)
     for i=1:numel(selectedElements)
    
%    mdV1FixneuTTC(:,i)=mean(mean(dV1FixneuTTC(:,:,[find(idx==i)]),3),2);
%     mdV1FixpuffTTC(:,i)=mean(mean(dV1FixpuffTTC(:,:,[find(idx==i)]),3),2);
%      mdV1FCneuTTC(:,i)=mean(mean(dV1FCneuTTC(:,:,[find(idx==i)]),3),2);
%       mdV1FCpuffTTC(:,i)=mean(mean(dV1FCpuffTTC(:,:,[find(idx==i)]),3),2);
      
%        mdV1FixneuTTC(:,i)=mean(dV1FixneuTTC(:,[find(idx==i)]),2);
%     mdV1FixpuffTTC(:,i)=mean(dV1FixpuffTTC(:,[find(idx==i)]),2);
%      mdV1FCneuTTCa(:,i)=mean(dV1FCneuTTCa(:,[find(idx==i)]),2);
%       mdV1FCpuffTTCa(:,i)=mean(dV1FCpuffTTCa(:,[find(idx==i)]),2);
      
%        mdV1FCneuTTCb(:,i)=mean(dV1FCneuTTCb(:,[find(idx==i)]),2);
%       mdV1FCpuffTTCb(:,i)=mean(dV1FCpuffTTCb(:,[find(idx==i)]),2);
% 
%        mdV1FixneuTTC(:,i)=mean(dV1FixneuTTC(:,[find(idx==i)]),2);
%       mdV1FixpuffTTC(:,i)=mean(dV1FixpuffTTC(:,[find(idx==i)]),2);
     
       mmdV1FCneuTTCb(:,i)=mean(dV1FCneuTTCb(:,[find(elecID==selectedElements(i))]),2);
      mmdV1FCpuffTTCb(:,i)=mean(dV1FCpuffTTCb(:,[find(elecID==selectedElements(i))]),2);

       mmdV1FixneuTTC(:,i)=mean(dV1FixneuTTC(:,[find(elecID==selectedElements(i))]),2);
      mmdV1FixpuffTTC(:,i)=mean(dV1FixpuffTTC(:,[find(elecID==selectedElements(i))]),2);
      
       mmdV1ori(i)=mean(dV1ori([find(elecID==selectedElements(i))]));
%              
     
      
       
     end
    mdV1FCneuTTCb= [mdV1FCneuTTCb mmdV1FCneuTTCb];
      mdV1FCpuffTTCb= [mdV1FCpuffTTCb mmdV1FCpuffTTCb];

       mdV1FixneuTTC=[mdV1FixneuTTC mmdV1FixneuTTC];
      mdV1FixpuffTTC=[mdV1FixpuffTTC mmdV1FixpuffTTC];
      
       mdV1ori=[mdV1ori mmdV1ori];
end

end
 
 
% for i=1:numel(validelec)
% 
% dV1FixneuTTC(:,:,i)=reshape(squeeze(V1Fixpsth(:,:,4,i,:)),[800 Fixusetrials]);
% dV1FCneuTTC(:,:,i)=reshape(squeeze(V1FCpsth(:,:,4,i,:)),[800 Fixusetrials]);
% dV1FixpuffTTC(:,:,i)=reshape(squeeze(V1Fixpsth(:,:,2,i,:)),[800 Fixusetrials]);
% dV1FCpuffTTC(:,:,i)=reshape(squeeze(V1FCpsth(:,:,2,i,:)),[800 Fixusetrials]);
%  end
 
%    mdV1FixneuTTC=squeeze(mean(dV1FixneuTTC,2));
%    mdV1FCneuTTC=squeeze(mean(dV1FCneuTTC,2));
%    mdV1FixpuffTTC=squeeze(mean(dV1FixpuffTTC,2));
%    mdV1FCpuffTTC=squeeze(mean(dV1FCpuffTTC,2));
 %%平滑
% smdV1FixneuTTC=convn(mdV1FixneuTTC,ones(smoothlength,1),'same')/smoothlength;
% smdV1FCneuTTCa=convn(mdV1FCneuTTCa,ones(smoothlength,1),'same')/smoothlength;
% % smdV1FixpuffTTC=convn(mdV1FixpuffTTC,ones(smoothlength,1),'same')/smoothlength;
% smdV1FCpuffTTCa=convn(mdV1FCpuffTTCa,ones(smoothlength,1),'same')/smoothlength;
% smdV1FixpuffTTC=mdV1FixpuffTTC;
% smdV1FCneuTTCb=mdV1FCneuTTCb;
% smdV1FixneuTTC=mdV1FixneuTTC;
% smdV1FCpuffTTCb=mdV1FCpuffTTCb;
smdV1FixpuffTTC=convn(mdV1FixpuffTTC,ones(smoothlength,1),'same')/smoothlength;
smdV1FCneuTTCb=convn(mdV1FCneuTTCb,ones(smoothlength,1),'same')/smoothlength;
smdV1FixneuTTC=convn(mdV1FixneuTTC,ones(smoothlength,1),'same')/smoothlength;
smdV1FCpuffTTCb=convn(mdV1FCpuffTTCb,ones(smoothlength,1),'same')/smoothlength;
% smoothwin=10;
% smdV1FixpuffTTC = filtfilt(ones(1,smoothwin)/smoothwin, 1, mdV1FixpuffTTC);
% smdV1FCneuTTCb = filtfilt(ones(1,smoothwin)/smoothwin, 1, mdV1FCneuTTCb);
% smdV1FixneuTTC = filtfilt(ones(1,smoothwin)/smoothwin, 1, mdV1FixneuTTC);
% smdV1FCpuffTTCb = filtfilt(ones(1,smoothwin)/smoothwin, 1, mdV1FCpuffTTCb);


% smdV1FixpuffTTC=convn(mdV1FixpuffTTC,ones(smoothlength,1),'same')/smoothlength;


% smdV1FCneuTTCb=mdV1FCneuTTCb;
% % smdV1FixpuffTTC=convn(mdV1FixpuffTTC,ones(smoothlength,1),'same')/smoothlength;
% smdV1FCpuffTTCb=mdV1FCpuffTTCb;
% 
% % smdV1FCneuTTCc=convn(mdV1FCneuTTCc,ones(smoothlength,1),'same')/smoothlength;
% % % smdV1FixpuffTTC=convn(mdV1FixpuffTTC,ones(smoothlength,1),'same')/smoothlength;
% % smdV1FCpuffTTCc=convn(mdV1FCpuffTTCc,ones(smoothlength,1),'same')/smoothlength;
% 
% smdV1FixneuTTC=mdV1FixneuTTC;
% % smdV1FixpuffTTC=convn(mdV1FixpuffTTC,ones(smoothlength,1),'same')/smoothlength;
% smdV1FixpuffTTC=mdV1FixpuffTTC;
%%可以看每个细胞的反应
if showcell==1
  j=1;  
for cellbin=1:9:size(mdV1ori,2)
figure;

for i=cellbin:cellbin+8%size(smdV1FixneuTTC,2)
subplot(3,3,i-(cellbin-1))
if i<=size(mdV1ori,2)
plot(mean(smdV1FCpuffTTCb(1:600,i),2).*1000,'-r','linewidth',1)
hold on;
plot(mean(smdV1FCneuTTCb(1:600,i),2).*1000,'-m','linewidth',1)
plot(mean(smdV1FixpuffTTC(1:600,i),2).*1000,'-g','linewidth',1)
plot(mean(smdV1FixneuTTC(1:600,i),2).*1000,'-b','linewidth',1)

title(['Ele' num2str(elecID(i)) ';' num2str(mdV1ori(i)) ])
% h=legend('FC-CS (puff)','FC-NS','Fix-CS','Fix-NS');
% set(h,'box','off')
% set(gca,'fontsize',15);
xlabel('Time(ms)')
% set(gca,'fontsize',20);
ylabel('FR(HZ)')%('Normalized activity')
% title(['All Block'])
% set(gca,'fontsize',20);
end
end
j=j+1;
end
end
% for i=1:size(mdV1FCneuTTC,2)
%     if max(smdV1FixneuTTC(:,i))<Fixfrth &&  max(smdV1FixpuffTTC(:,i))<Fixfrth
%         excidx(i)=1;
%     elseif max(smdV1FCpuffTTC(:,i))<FCfrth && max(smdV1FCneuTTC(:,i))<FCfrth
%          excidx(i)=2;
%     elseif max(smdV1FCpuffTTC(:,i))>bFCfrth && max(smdV1FCneuTTC(:,i))>bFCfrth
%          excidx(i)=3;
%     else
%          excidx(i)=0;
%     end
% end
% smdV1FixneuTTC(:,find(excidx>0))=[];
% smdV1FixpuffTTC(:,find(excidx>0))=[];
% smdV1FCneuTTC(:,find(excidx>0))=[];
% smdV1FCpuffTTC(:,find(excidx>0))=[];

%%标准化  0为不去基线  1为去基线   3 只去基线 4为不标准化
if cutbase==0
% NsmdV1FixneuTTC=smdV1FixneuTTC./repmat(max(smdV1FixneuTTC),[size(smdV1FixneuTTC,1),1]);
% NsmdV1FCneuTTC=smdV1FCneuTTC./repmat(max(smdV1FixneuTTC),[size(smdV1FCneuTTC,1),1]);
% NsmdV1FixpuffTTC=smdV1FixpuffTTC./repmat(max(smdV1FixneuTTC),[size(smdV1FixpuffTTC,1),1]);
% NsmdV1FCpuffTTC=smdV1FCpuffTTC./repmat(max(smdV1FixneuTTC),[size(smdV1FCpuffTTC,1),1]);


% NsmdV1FCneuTTCa=smdV1FCneuTTCa./repmat(max(smdV1FCpuffTTCa),[size(smdV1FCneuTTCa,1),1]);
% NsmdV1FCpuffTTCa=smdV1FCpuffTTCa./repmat(max(smdV1FCpuffTTCa),[size(smdV1FCpuffTTCa,1),1]);

NsmdV1FCneuTTCb=smdV1FCneuTTCb./repmat(max(smdV1FixneuTTC),[size(smdV1FCneuTTCb,1),1]);
NsmdV1FCpuffTTCb=smdV1FCpuffTTCb./repmat(max(smdV1FixneuTTC),[size(smdV1FCpuffTTCb,1),1]);

NsmdV1FixneuTTC=smdV1FixneuTTC./repmat(max(smdV1FixneuTTC),[size(smdV1FixneuTTC,1),1]);
NsmdV1FixpuffTTC=smdV1FixpuffTTC./repmat(max(smdV1FixneuTTC),[size(smdV1FixpuffTTC,1),1]);

% NsmdV1FCneuTTCd=smdV1FCneuTTCd./repmat(max(smdV1FCpuffTTCa),[size(smdV1FCneuTTCd,1),1]);
% NsmdV1FCpuffTTCd=smdV1FCpuffTTCd./repmat(max(smdV1FCpuffTTCa),[size(smdV1FCpuffTTCd,1),1]);

elseif cutbase==1

% NsmdV1FixneuTTC=(smdV1FixneuTTC-repmat(mean(smdV1FixneuTTC(31:200,:)),[size(smdV1FixneuTTC,1),1]))./repmat(max(smdV1FixneuTTC),[size(smdV1FixneuTTC,1),1]);
% NsmdV1FCneuTTC=(smdV1FCneuTTC-repmat(mean(smdV1FCneuTTC(31:200,:)),[size(smdV1FCneuTTC,1),1]))./repmat(max(smdV1FixneuTTC),[size(smdV1FCneuTTC,1),1]);
% NsmdV1FixpuffTTC=(smdV1FixpuffTTC-repmat(mean(smdV1FixpuffTTC(31:200,:)),[size(smdV1FixpuffTTC,1),1]))./repmat(max(smdV1FixneuTTC),[size(smdV1FixpuffTTC,1),1]);
% NsmdV1FCpuffTTC=(smdV1FCpuffTTC-repmat(mean(smdV1FCpuffTTC(31:200,:)),[size(smdV1FCpuffTTC,1),1]))./repmat(max(smdV1FixneuTTC),[size(smdV1FCpuffTTC,1),1]);

% 
% NsmdV1FCneuTTCa=(smdV1FCneuTTCa-repmat(mean(smdV1FCneuTTCa(21:220,:)),[size(smdV1FCneuTTCa,1),1]))./repmat(max(smdV1FCpuffTTCa),[size(smdV1FCneuTTCa,1),1]);
% NsmdV1FCpuffTTCa=(smdV1FCpuffTTCa-repmat(mean(smdV1FCpuffTTCa(21:220,:)),[size(smdV1FCpuffTTCa,1),1]))./repmat(max(smdV1FCpuffTTCa),[size(smdV1FCpuffTTCa,1),1]);

NsmdV1FCneuTTCb=(smdV1FCneuTTCb-repmat(mean(smdV1FCneuTTCb(norwin,:)),[size(smdV1FCneuTTCb,1),1]))./repmat(max(smdV1FixneuTTC),[size(smdV1FCneuTTCb,1),1]);
NsmdV1FCpuffTTCb=(smdV1FCpuffTTCb-repmat(mean(smdV1FCpuffTTCb(norwin,:)),[size(smdV1FCpuffTTCb,1),1]))./repmat(max(smdV1FixneuTTC),[size(smdV1FCpuffTTCb,1),1]);

NsmdV1FixpuffTTC=(smdV1FixpuffTTC-repmat(mean(smdV1FixpuffTTC(norwin,:)),[size(smdV1FixpuffTTC,1),1]))./repmat(max(smdV1FixneuTTC),[size(smdV1FixpuffTTC,1),1]);
NsmdV1FixneuTTC=(smdV1FixneuTTC-repmat(mean(smdV1FixneuTTC(norwin,:)),[size(smdV1FixneuTTC,1),1]))./repmat(max(smdV1FixneuTTC),[size(smdV1FixneuTTC,1),1]);
% NsmdV1FCneuTTCd=(smdV1FCneuTTCd-repmat(mean(smdV1FCneuTTCd(31:200,:)),[size(smdV1FCneuTTCd,1),1]))./repmat(max(smdV1FCpuffTTCa),[size(smdV1FCneuTTCd,1),1]);
% NsmdV1FCpuffTTCd=(smdV1FCpuffTTCd-repmat(mean(smdV1FCpuffTTCd(31:200,:)),[size(smdV1FCpuffTTCd,1),1]))./repmat(max(smdV1FCpuffTTCa),[size(smdV1FCpuffTTCd,1),1]);
%  smconpuffpsth=(smconpuffpsth-repmat(mean(smconpuffpsth(1:200,:)),[size(smconpuffpsth,1),1]))./repmat(max(smoripuffpsth),[size(smconpuffpsth,1),1]);
%  smconneupsth=(smconneupsth-repmat(mean(smconneupsth(1:200,:)),[size(smconneupsth,1),1]))./repmat(max(smorineupsth),[size(smconneupsth,1),1]);
%  smoripuffpsth=(smoripuffpsth-repmat(mean(smoripuffpsth(1:200,:)),[size(smoripuffpsth,1),1]))./repmat(max(smorineupsth),[size(smoripuffpsth,1),1]);
%  smorineupsth=(smorineupsth-repmat(mean(smorineupsth(1:200,:)),[size(smorineupsth,1),1]))./repmat(max(smorineupsth),[size(smorineupsth,1),1]);
elseif cutbase==3

% NsmdV1FixneuTTC=(smdV1FixneuTTC-repmat(mean(smdV1FixneuTTC(31:200,:)),[size(smdV1FixneuTTC,1),1]))./repmat(max(smdV1FixneuTTC),[size(smdV1FixneuTTC,1),1]);
% NsmdV1FCneuTTC=(smdV1FCneuTTC-repmat(mean(smdV1FCneuTTC(31:200,:)),[size(smdV1FCneuTTC,1),1]))./repmat(max(smdV1FixneuTTC),[size(smdV1FCneuTTC,1),1]);
% NsmdV1FixpuffTTC=(smdV1FixpuffTTC-repmat(mean(smdV1FixpuffTTC(31:200,:)),[size(smdV1FixpuffTTC,1),1]))./repmat(max(smdV1FixneuTTC),[size(smdV1FixpuffTTC,1),1]);
% NsmdV1FCpuffTTC=(smdV1FCpuffTTC-repmat(mean(smdV1FCpuffTTC(31:200,:)),[size(smdV1FCpuffTTC,1),1]))./repmat(max(smdV1FixneuTTC),[size(smdV1FCpuffTTC,1),1]);

% 
% NsmdV1FCneuTTCa=(smdV1FCneuTTCa-repmat(mean(smdV1FCneuTTCa(21:220,:)),[size(smdV1FCneuTTCa,1),1]))./repmat(max(smdV1FCpuffTTCa),[size(smdV1FCneuTTCa,1),1]);
% NsmdV1FCpuffTTCa=(smdV1FCpuffTTCa-repmat(mean(smdV1FCpuffTTCa(21:220,:)),[size(smdV1FCpuffTTCa,1),1]))./repmat(max(smdV1FCpuffTTCa),[size(smdV1FCpuffTTCa,1),1]);

NsmdV1FCneuTTCb=(smdV1FCneuTTCb-repmat(mean(smdV1FCneuTTCb(norwin,:)),[size(smdV1FCneuTTCb,1),1]));
NsmdV1FCpuffTTCb=(smdV1FCpuffTTCb-repmat(mean(smdV1FCpuffTTCb(norwin,:)),[size(smdV1FCpuffTTCb,1),1]));

NsmdV1FixpuffTTC=(smdV1FixpuffTTC-repmat(mean(smdV1FixpuffTTC(norwin,:)),[size(smdV1FixpuffTTC,1),1]));
NsmdV1FixneuTTC=(smdV1FixneuTTC-repmat(mean(smdV1FixneuTTC(norwin,:)),[size(smdV1FixneuTTC,1),1]));
% NsmdV1FCneuTTCd=(smdV1FCneuTTCd-repmat(mean(smdV1FCneuTTCd(31:200,:)),[size(smdV1FCneuTTCd,1),1]))./repmat(max(smdV1FCpuffTTCa),[size(smdV1FCneuTTCd,1),1]);
% NsmdV1FCpuffTTCd=(smdV1FCpuffTTCd-repmat(mean(smdV1FCpuffTTCd(31:200,:)),[size(smdV1FCpuffTTCd,1),1]))./repmat(max(smdV1FCpuffTTCa),[size(smdV1FCpuffTTCd,1),1]);
%  smconpuffpsth=(smconpuffpsth-repmat(mean(smconpuffpsth(1:200,:)),[size(smconpuffpsth,1),1]))./repmat(max(smoripuffpsth),[size(smconpuffpsth,1),1]);
%  smconneupsth=(smconneupsth-repmat(mean(smconneupsth(1:200,:)),[size(smconneupsth,1),1]))./repmat(max(smorineupsth),[size(smconneupsth,1),1]);
%  smoripuffpsth=(smoripuffpsth-repmat(mean(smoripuffpsth(1:200,:)),[size(smoripuffpsth,1),1]))./repmat(max(smorineupsth),[size(smoripuffpsth,1),1]);
%  smorineupsth=(smorineupsth-repmat(mean(smorineupsth(1:200,:)),[size(smorineupsth,1),1]))./repmat(max(smorineupsth),[size(smorineupsth,1),1]);


elseif cutbase==4
% NsmdV1FixneuTTC=smdV1FixneuTTC;
% NsmdV1FCneuTTC=smdV1FCneuTTC;
% NsmdV1FixpuffTTC=smdV1FixpuffTTC;
% NsmdV1FCpuffTTC=smdV1FCpuffTTC;

% NsmdV1FCneuTTCa=smdV1FCneuTTCa;
% NsmdV1FCpuffTTCa=smdV1FCpuffTTCa;

NsmdV1FCneuTTCb=smdV1FCneuTTCb;
NsmdV1FCpuffTTCb=smdV1FCpuffTTCb;

NsmdV1FixneuTTC=smdV1FixneuTTC;
NsmdV1FixpuffTTC=smdV1FixpuffTTC;

% NsmdV1FCneuTTCd=smdV1FCneuTTCd;
% NsmdV1FCpuffTTCd=smdV1FCpuffTTCd;

end
if norn==0
NsmdV1FCneuTTCb=1000*NsmdV1FCneuTTCb;
NsmdV1FCpuffTTCb=1000*NsmdV1FCpuffTTCb;

NsmdV1FixneuTTC=1000*NsmdV1FixneuTTC;
NsmdV1FixpuffTTC=1000*NsmdV1FixpuffTTC;
else
    NsmdV1FCneuTTCb=1*NsmdV1FCneuTTCb;
NsmdV1FCpuffTTCb=1*NsmdV1FCpuffTTCb;

NsmdV1FixneuTTC=1*NsmdV1FixneuTTC;
NsmdV1FixpuffTTC=1*NsmdV1FixpuffTTC;

end

% pre=find(mdV1ori>22.5  & mdV1ori<67.5);
% ot=find(mdV1ori>112.5  & mdV1ori<157.5);
% 
% NsmdV1FixneuTTC=NsmdV1FixneuTTC(:,pre);
% NsmdV1FCneuTTC=NsmdV1FCneuTTC(:,pre);
% NsmdV1FixpuffTTC=NsmdV1FixpuffTTC(:,pre);
% NsmdV1FCpuffTTC=NsmdV1FCpuffTTC(:,pre);
%%无关
mmpFCpuff=mean(mpFCpuff);
mstdpFCpuff=mean(stdpFCpuff);

mmpFCneu=mean(mpFCneu);
mstdpFCneu=mean(stdpFCneu);

%%

% NsmdV1FixneuTTC=NsmdV1FixneuTTC(:,ot);
% NsmdV1FCneuTTC=NsmdV1FCneuTTC(:,ot);
% NsmdV1FixpuffTTC=NsmdV1FixpuffTTC(:,ot);
% NsmdV1FCpuffTTC=NsmdV1FCpuffTTC(:,ot);

%%
sitime=[];
Fixdiff=(mean(NsmdV1FixpuffTTC(1:600,:),2)-mean(NsmdV1FixneuTTC(1:600,:),2));%./(mean(NsmdV1FixpuffTTC(1:700,:),2)+mean(NsmdV1FixneuTTC(1:700,:),2));
FCdiff=(mean(NsmdV1FCpuffTTCb(1:600,:),2)-mean(NsmdV1FCneuTTCb(1:600,:),2));%./ (mean(NsmdV1FCpuffTTC(1:700,:),2)+mean(NsmdV1FCneuTTC(1:700,:),2));

puffdiff=mean(NsmdV1FCpuffTTCb(1:600,:),2)-mean(NsmdV1FixpuffTTC(1:600,:),2);%./(mean(NsmdV1FixpuffTTC(1:700,:),2)+mean(NsmdV1FixneuTTC(1:700,:),2));
neudiff=mean(NsmdV1FCneuTTCb(1:600,:),2)-mean(NsmdV1FixneuTTC(1:600,:),2);

iFixdiff=NsmdV1FixpuffTTC(1:600,:)-NsmdV1FixneuTTC(1:600,:);%./(mean(NsmdV1FixpuffTTC(1:700,:),2)+mean(NsmdV1FixneuTTC(1:700,:),2));
iFCdiff=NsmdV1FCpuffTTCb(1:600,:)-NsmdV1FCneuTTCb(1:600,:);

ipuffdiff=NsmdV1FCpuffTTCb(1:600,:)-NsmdV1FixpuffTTC(1:600,:);%./(mean(NsmdV1FixpuffTTC(1:700,:),2)+mean(NsmdV1FixneuTTC(1:700,:),2));
ineudiff=NsmdV1FCneuTTCb(1:600,:)-NsmdV1FixneuTTC(1:600,:);

iFC_Fixdiff=iFCdiff-iFixdiff;
% ipuffdiff=NsmdV1FCpuffTTC4c(1:600,:)-NsmdV1FixpuffTTC4(1:600,:);%./(mean(NsmdV4FixpuffTTC(1:700,:),2)+mean(NsmdV4FixneuTTC(1:700,:),2));
% ineudiff=NsmdV1FCneuTTC4a(1:600,:)-NsmdV1FixneuTTC4(1:600,:);
% markmiFixdiff=NsmdV1FixpuffTTC(241:256,:)-NsmdV1FixneuTTC(241:256,:);%./(mean(NsmdV1FixpuffTTC(1:700,:),2)+mean(NsmdV1FixneuTTC(1:700,:),2));
markiFCdiff=mean((NsmdV1FCpuffTTCb(241:280,:)-NsmdV1FCneuTTCb(241:280,:)),1);
mmarkiFCdiff=mean(markiFCdiff);
stdmarkiFCdiff=std(markiFCdiff);
% ipuffdiff=NsmdV1FCpuffTTCb(1:600,:)-NsmdV1FixpuffTTC(1:600,:);%./(mean(NsmdV1FixpuffTTC(1:700,:),2)+mean(NsmdV1FixneuTTC(1:700,:),2));
% ineudiff=NsmdV1FCneuTTCb(1:600,:)-NsmdV1FixneuTTC(1:600,:);
stwin=[];
 swin=10;
 for stwin=200:10:500%5:5:550   %222:248:257    260:295   295:320  330:355
% [a1,b1]=signrank(mean(NsmdV1FCneuTTCa(stwin:stwin+swin,:),1),mean(NsmdV1FixneuTTCc(stwin:stwin+swin,:),1));
[a2,b2]=signrank(mean(NsmdV1FCpuffTTCb(stwin:stwin+swin,:),1),mean(NsmdV1FCneuTTCb(stwin:stwin+swin,:),1));

[a3,b3]=signrank(mean(NsmdV1FixpuffTTC(stwin:stwin+swin,:),1),mean(NsmdV1FixneuTTC(stwin:stwin+swin,:),1));
% [a4,b5]=signrank(mean(NsmdV1FCpuffTTCb(stwin:stwin+swin,:),1),mean(NsmdV1FCpuffTTCc(stwin:stwin+swin,:),1));

%  [a6,b6]=signrank(mean(iFixdiff(stwin:stwin+swin,:),1),mean(iFCdiff(stwin:stwin+swin,:),1));
%  [a7,b7]=signrank(mean(npuffdiff(stwin:stwin+swin,:),1),mean(nneudiff(stwin:stwin+swin,:),1));
 
% %    [a6,b6]=signrank(mean(iFixdiff(154:174,:),1),mean(iFCdiff(154:174,:),1));
if a3<0.001
    sitime(i)=stwin;
    i=i+1;
end
% if a7<0.001
%     sitime2(j)=stwin;
%     j=j+1;
end
%  end
yy=-0.01*ones(1,numel(sitime));

%%

FCpufferr=std(NsmdV1FCpuffTTCb(1:600,:),0,2)/sqrt(size(NsmdV1FCpuffTTCb(1:600,:),2));
FCneuerr=std(NsmdV1FCneuTTCb(1:600,:),0,2)/sqrt(size(NsmdV1FCneuTTCb(1:600,:),2));
Fixpufferr=std(NsmdV1FixpuffTTC(1:600,:),0,2)/sqrt(size(NsmdV1FixpuffTTC(1:600,:),2));
Fixneuerr=std(NsmdV1FixneuTTC(1:600,:),0,2)/sqrt(size(NsmdV1FixneuTTC(1:600,:),2));

xv=(-199:400)';
yFCpuff=mean(NsmdV1FCpuffTTCb(1:600,:),2);
yFCneu=mean(NsmdV1FCneuTTCb(1:600,:),2);
yFixpuff=mean(NsmdV1FixpuffTTC(1:600,:),2);
yFixneu=mean(NsmdV1FixneuTTC(1:600,:),2);


%%
figure;
% yyaxis left
hold on;

h3=plot(xv,yFixpuff,'-g','linewidth',2.5);
patch([xv; flipud(xv)],[yFixpuff+Fixpufferr; flipud(yFixpuff-Fixpufferr)],'g','EdgeColor', 'none','FaceAlpha', 0.3);
% plot(mean(NsmdV1FCneuTTCb(1:600,:),2),'-b','linewidth',2.5)
h4=plot(xv,yFixneu,'-b','linewidth',2.5);
patch([xv; flipud(xv)],[yFixneu+Fixneuerr; flipud(yFixneu-Fixneuerr)],'b','EdgeColor', 'none','FaceAlpha', 0.3);

h1=plot(xv,yFCpuff,'-r','linewidth',2.5);
patch([xv; flipud(xv)],[yFCpuff+FCpufferr; flipud(yFCpuff-FCpufferr)],'r','EdgeColor', 'none','FaceAlpha', 0.3);

h2=plot(xv,yFCneu,'-m','linewidth',2.5);
patch([xv; flipud(xv)],[yFCneu+FCneuerr; flipud(yFCneu-FCneuerr)],'m','EdgeColor', 'none','FaceAlpha', 0.3);
% plot(mean(NsmdV1FCpuffTTCb(1:600,:),2),'-b','linewidth',2.5)
% 
% plot(mean(NsmdV1FCpuffTTCd(1:600,:),2),'-r','linewidth',2.5)

% plot(mean(NsmdV1FCneuTTCd(1:600,:),2),'-r','linewidth',2.5)
% plot(sitime,yy,'k*')

% plot(sitime-195,yy,'k*')
h=legend([h1,h2,h3,h4],'FC-CS (puff)','FC-NS','Fix-CS','Fix-NS');
set(h,'box','off')
set(gca,'fontsize',15);
xlabel('Time(ms)')
set(gca,'fontsize',20);
ylabel('Normalized activity')%ylabel('FR(Hz)')
% title(['All Block'])
set(gca,'fontsize',20);
xt=[-200:100:400];

% set(gca,'xtick',xt);
set(gca,'xticklabel',xt);


% ylim([-0.1,1.1])

% significant = [0, 1, 0, 1, 0, 1]; 
% 
% %% 3. 底部画显著方块（核心代码）
% block_height = 0.1;  % 方块高度
% block_width  = 0.8;  % 方块宽度
% y_bottom     = -0.2; % 方块离图底部距离
% 
% for i = 1:length(xv)
%     pos_x = x(i) - block_width/2;
%     pos_y = y_bottom;
%     w = block_width;
%     h = block_height;
%     
%     if significant(i) == 1
%         % 显著：黑色实心方块
%         rectangle('Position',[pos_x, pos_y, w, h],...
%                   'FaceColor','k','EdgeColor','k');
%     else
%         % 不显著：白色空心方块
%         rectangle('Position',[pos_x, pos_y, w, h],...
%                   'FaceColor','w','EdgeColor','k');
%     end
% end
% 




sitime=[];
sitime2=[];
sitime3=[];
 i=1;
 j=1;
 swin=20;
 for stwin=160:20:400%5:5:550   %222:248:257    260:295   295:320  330:355
% [a1,b1]=signrank(mean(NsmdV4FCneuTTCa(stwin:stwin+swin,:),1),mean(NsmdV4FixneuTTCc(stwin:stwin+swin,:),1));
% [a2,b2]=signrank(mean(NsmdV4FCpuffTTCa(stwin:stwin+swin,:),1),mean(NsmdV4FCpuffTTCb(stwin:stwin+swin,:),1));
% 
% [a3,b3]=signrank(mean(NsmdV4FCpuffTTCa(stwin:stwin+swin,:),1),mean(NsmdV4FCpuffTTCc(stwin:stwin+swin,:),1));
% [a4,b5]=signrank(mean(NsmdV4FCpuffTTCb(stwin:stwin+swin,:),1),mean(NsmdV4FCpuffTTCc(stwin:stwin+swin,:),1));

 [a6(j),b6(j),z6(j)]=signrank(mean(ipuffdiff(stwin:stwin+swin,:),1),mean(ineudiff(stwin:stwin+swin,:),1));
 [a61,b61]=ranksum(mean(iFixdiff(stwin:stwin+swin,:),1),zeros(1,size(iFixdiff,2)));
  [a7,b7]=ranksum(mean(iFixdiff(stwin:stwin+swin,:),1),mean(iFCdiff(stwin:stwin+swin,:),1));
%  [a7,b7]=signrank(mean(npuffdiff(stwin:stwin+swin,:),1),mean(nneudiff(stwin:stwin+swin,:),1));
 
% %    [a6,b6]=signrank(mean(iFixdiff(154:174,:),1),mean(iFCdiff(154:174,:),1));
if a6(j)<0.01
    sitime2(i)=stwin;
    i=i+1;
end

% if a7<0.01
%     sitime3(i)=stwin;
%     i=i+1;
% end
% if a7<0.001
%     sitime2(j)=stwin;
    j=j+1;
 end
 
 adjp=mafdr(a6,'BHFDR', true);
isgi=a6<(0.05/21);
% iesgi2=[z6.zval]>0.1;
isgi2=adjp<0.05;
timee=200:20:400;
yy=-0.002*ones(1,numel(sitime));
yy2=-0.002*ones(1,numel(sitime2));
yy3=-0.002*ones(1,numel(sitime3));






%%%%

iFCerr=std(iFCdiff(1:600,:),0,2)/sqrt(size(iFCdiff(1:600,:),2));
iFixerr=std(iFixdiff(1:600,:),0,2)/sqrt(size(iFixdiff(1:600,:),2));
ipufferr=std(ipuffdiff(1:600,:),0,2)/sqrt(size(ipuffdiff(1:600,:),2));
ineuerr=std(ineudiff(1:600,:),0,2)/sqrt(size(ineudiff(1:600,:),2));

xv=(-199:400)';
ypuffdif=mean(ipuffdiff(1:600,:),2);
yneudif=mean(ineudiff(1:600,:),2);

figure;
% yyaxis left
hold on;
h1=plot(xv,ypuffdif,'-r','linewidth',2.5);
patch([xv; flipud(xv)],[ypuffdif+ipufferr; flipud(ypuffdif-ipufferr)],'r','EdgeColor', 'none','FaceAlpha', 0.3);

% h2=plot(xv,yFCneu,'-m','linewidth',2.5);
% patch([xv; flipud(xv)],[yFCneu+FCneuerr; flipud(yFCneu-FCneuerr)],'m','EdgeColor', 'none','FaceAlpha', 0.3);
% plot(mean(NsmdV1FCpuffTTCb(1:600,:),2),'-b','linewidth',2.5)

% plot(mean(NsmdV1FCpuffTTCd(1:600,:),2),'-r','linewidth',2.5)

h2=plot(xv,yneudif,'-g','linewidth',2.5);
patch([xv; flipud(xv)],[yneudif+ineuerr; flipud(yneudif-ineuerr)],'g','EdgeColor', 'none','FaceAlpha', 0.3);
% plot(sitime2-189,yy2,'k*')


for i = 1:length(timee)
    if isgi2(i) == 1
        % 在显著时间点画一个小矩形
        text(timee(i)-200,0, '*','FontSize', 18, ...         % 星号大小（14、18、22 随便调）
    'HorizontalAlignment','center')
    end
end
% plot(mean(NsmdV1FCneuTTCb(1:600,:),2),'-b','linewidth',2.5)
% h4=plot(xv,yFixneu,'-b','linewidth',2.5);
% patch([xv; flipud(xv)],[yFixneu+Fixneuerr; flipud(yFixneu-Fixneuerr)],'b','EdgeColor', 'none','FaceAlpha', 0.3);
% % plot(mean(NsmdV1FCneuTTCd(1:600,:),2),'-r','linewidth',2.5)
% plot(sitime,yy,'k*')
h=legend([h1,h2],'FCCS-FixCS (CS)','FCNS-FixNS (NS)');
set(h,'box','off')
set(gca,'fontsize',15);
xlabel('Time(ms)')
set(gca,'fontsize',20);
 ylabel('Normalized activity')
% ylim([-0.06 0.06])
% title(['All Block'])
set(gca,'fontsize',20);


% figure;
% hold on
% CSdiff=((mean(NsmdV1FCneuTTCb(1:600,:),2)-mean(NsmdV1FixneuTTC(1:600,:),2)));% ./(mean(NsmdV1FixneuTTC(1:700,:),2));%+mean(NsmdV1FixneuTTC(1:700,:),2));
% NSdiff=((mean(NsmdV1FCpuffTTCb(1:600,:),2)-mean(NsmdV1FixpuffTTC(1:600,:),2))); %./ (mean(NsmdV1FixpuffTTC(1:700,:),2));%+mean(NsmdV1FCneuTTC(1:700,:),2));
% 
% % line([1,700],[0,0],'linestyle','-');
% ylim([-0.2 0.2])
% 
% plot(CSdiff,'-r','linewidth',1.5)
% plot(NSdiff,'-g','linewidth',1.5)
% plot(sitime3,yy3,'k*')
% h=legend('FCCS-FixCS','FCNS-FixNS');
% 
% 
% line([1,600],[0,0],'linestyle','-');
% set(h,'box','off')
% rx=[230 230 265 265];
% ry=[0.2 -0.2 -0.2 0.2];
% fill(rx,ry,[0.1 0.1 0.1],'FaceAlpha',0.2,'EdgeAlpha',0.2)
% set(gca,'fontsize',15);
% xlabel('Time(ms)')
% set(gca,'fontsize',20);
% ylabel('Normalized activity')
% % title(['All Block'])
% set(gca,'fontsize',20);
% xt=[-200:100:500];
% % set(gca,'xtick',xt);
% set(gca,'xticklabel',xt);
% xt=[-200:100:500];
% % set(gca,'xtick',xt);
% set(gca,'xticklabel',xt);
% % 
% % 
% % 
% % 
% % % stwin=245:275  ;  %222:248:257    260:295   295:320  330:355
% % [a1,b1]=signrank(mean(NsmdV1FCneuTTC(stwin,:),1),mean(NsmdV1FixneuTTC(stwin,:),1));
% % [a2,b2]=signrank(mean(NsmdV1FCpuffTTC(stwin,:),1),mean(NsmdV1FixpuffTTC(stwin,:),1));
% % [a3,b3]=signrank(mean(NsmdV1FCpuffTTC(stwin,:),1)-mean(NsmdV1FixpuffTTC(stwin,:),1),mean(NsmdV1FCneuTTC(stwin,:),1)-mean(NsmdV1FixneuTTC(stwin,:),1));
% % [a2,b2]=signrank()
% 
% yaya=mean(obardiff(230:265)-nbardiff(230:265));
sitime=[];
sitime2=[];
sitime3=[];
 i=1;
 j=1;
 swin=20;
 for stwin=200:20:400%5:5:550   %222:248:257    260:295   295:320  330:355
% [a1,b1]=signrank(mean(NsmdV4FCneuTTCa(stwin:stwin+swin,:),1),mean(NsmdV4FixneuTTCc(stwin:stwin+swin,:),1));
% [a2,b2]=signrank(mean(NsmdV4FCpuffTTCa(stwin:stwin+swin,:),1),mean(NsmdV4FCpuffTTCb(stwin:stwin+swin,:),1));
% 
% [a3,b3]=signrank(mean(NsmdV4FCpuffTTCa(stwin:stwin+swin,:),1),mean(NsmdV4FCpuffTTCc(stwin:stwin+swin,:),1));
% [a4,b5]=signrank(mean(NsmdV4FCpuffTTCb(stwin:stwin+swin,:),1),mean(NsmdV4FCpuffTTCc(stwin:stwin+swin,:),1));

 [a6(j),b6(j),z6(j)]=signrank(mean(iFixdiff(stwin:stwin+swin,:),1),mean(iFCdiff(stwin:stwin+swin,:),1));
 [a61,b61]=ranksum(mean(iFixdiff(stwin:stwin+swin,:),1),zeros(1,size(iFixdiff,2)));
  [a7,b7]=ranksum(mean(iFixdiff(stwin:stwin+swin,:),1),mean(iFCdiff(stwin:stwin+swin,:),1));
%  [a7,b7]=signrank(mean(npuffdiff(stwin:stwin+swin,:),1),mean(nneudiff(stwin:stwin+swin,:),1));
 
% %    [a6,b6]=signrank(mean(iFixdiff(154:174,:),1),mean(iFCdiff(154:174,:),1));
if a6(j)<0.01
    sitime2(i)=stwin;
    i=i+1;
end

% if a7<0.01
%     sitime3(i)=stwin;
%     i=i+1;
% end
% if a7<0.001
%     sitime2(j)=stwin;
    j=j+1;
 end
 
 adjp=mafdr(a6,'BHFDR', true);
isgi=a6<(0.05/21);
% iesgi2=[z6.zval]>0.1;
isgi2=adjp<0.05;
timee=200:20:400;
yy=-0.002*ones(1,numel(sitime));
yy2=-0.002*ones(1,numel(sitime2));
yy3=-0.002*ones(1,numel(sitime3));






%%%%

iFCerr=std(iFCdiff(1:600,:),0,2)/sqrt(size(iFCdiff(1:600,:),2));
iFixerr=std(iFixdiff(1:600,:),0,2)/sqrt(size(iFixdiff(1:600,:),2));


xv=(-199:400)';
yFCdif=mean(iFCdiff(1:600,:),2);
yFixdif=mean(iFixdiff(1:600,:),2);

figure;
% yyaxis left
hold on;
h1=plot(xv,yFCdif,'-r','linewidth',2.5);
patch([xv; flipud(xv)],[yFCdif+iFCerr; flipud(yFCdif-iFCerr)],'r','EdgeColor', 'none','FaceAlpha', 0.3);

% h2=plot(xv,yFCneu,'-m','linewidth',2.5);
% patch([xv; flipud(xv)],[yFCneu+FCneuerr; flipud(yFCneu-FCneuerr)],'m','EdgeColor', 'none','FaceAlpha', 0.3);
% plot(mean(NsmdV1FCpuffTTCb(1:600,:),2),'-b','linewidth',2.5)

% plot(mean(NsmdV1FCpuffTTCd(1:600,:),2),'-r','linewidth',2.5)

h2=plot(xv,yFixdif,'-g','linewidth',2.5);
patch([xv; flipud(xv)],[yFixdif+iFixerr; flipud(yFixdif-iFixerr)],'g','EdgeColor', 'none','FaceAlpha', 0.3);
% plot(sitime2-189,yy2,'k*')


for i = 1:length(timee)
    if isgi2(i) == 1
        % 在显著时间点画一个小矩形
        text(timee(i)-190,0, '*','FontSize', 18, ...         % 星号大小（14、18、22 随便调）
    'HorizontalAlignment','center')
    end
end
% plot(mean(NsmdV1FCneuTTCb(1:600,:),2),'-b','linewidth',2.5)
% h4=plot(xv,yFixneu,'-b','linewidth',2.5);
% patch([xv; flipud(xv)],[yFixneu+Fixneuerr; flipud(yFixneu-Fixneuerr)],'b','EdgeColor', 'none','FaceAlpha', 0.3);
% % plot(mean(NsmdV1FCneuTTCd(1:600,:),2),'-r','linewidth',2.5)
% plot(sitime,yy,'k*')
h=legend([h1,h2],'FCCS-FCNS (Condition)','FixCS-FixNS (Fix)');
set(h,'box','off')
set(gca,'fontsize',15);
xlabel('Time(ms)')
set(gca,'fontsize',20);
ylabel('Normalized activity')
% title(['All Block'])
% ylim([-0.06 0.06])
set(gca,'fontsize',20);


iFCerr=std(iFC_Fixdiff(1:600,:),0,2)/sqrt(size(iFC_Fixdiff(1:600,:),2));
iFCerr=std(iFCdiff(1:600,:),0,2)/sqrt(size(iFCdiff(1:600,:),2));
% iFixerr=std(iFixdiff(1:600,:),0,2)/sqrt(size(iFixdiff(1:600,:),2));


xv=(-199:400)';
yFCdif=mean(iFC_Fixdiff(1:600,:),2);
yFixdif=mean(iFixdiff(1:600,:),2);

figure;
% yyaxis left
hold on;
h1=plot(xv,yFCdif,'-r','linewidth',2.5);
patch([xv; flipud(xv)],[yFCdif+iFCerr; flipud(yFCdif-iFCerr)],'r','EdgeColor', 'none','FaceAlpha', 0.3);

% h2=plot(xv,yFCneu,'-m','linewidth',2.5);
% patch([xv; flipud(xv)],[yFCneu+FCneuerr; flipud(yFCneu-FCneuerr)],'m','EdgeColor', 'none','FaceAlpha', 0.3);
% plot(mean(NsmdV1FCpuffTTCb(1:600,:),2),'-b','linewidth',2.5)

% plot(mean(NsmdV1FCpuffTTCd(1:600,:),2),'-r','linewidth',2.5)

% h2=plot(xv,yFixdif,'-g','linewidth',2.5);
% patch([xv; flipud(xv)],[yFixdif+iFixerr; flipud(yFixdif-iFixerr)],'g','EdgeColor', 'none','FaceAlpha', 0.3);
% plot(sitime2-189,yy2,'k*')


% for i = 1:length(timee)
%     if isgi2(i) == 1
%         % 在显著时间点画一个小矩形
%         text(timee(i)-190,0, '*','FontSize', 18, ...         % 星号大小（14、18、22 随便调）
%     'HorizontalAlignment','center')
%     end
% end
% plot(mean(NsmdV1FCneuTTCb(1:600,:),2),'-b','linewidth',2.5)
% h4=plot(xv,yFixneu,'-b','linewidth',2.5);
% patch([xv; flipud(xv)],[yFixneu+Fixneuerr; flipud(yFixneu-Fixneuerr)],'b','EdgeColor', 'none','FaceAlpha', 0.3);
% % plot(mean(NsmdV1FCneuTTCd(1:600,:),2),'-r','linewidth',2.5)
% plot(sitime,yy,'k*')
h=legend([h1],'FCCS-FCNS (Condition) - FixCS-FixNS (Fix)');
set(h,'box','off')
set(gca,'fontsize',15);
xlabel('Time(ms)')
set(gca,'fontsize',20);
if norn==0
ylabel('FR(Hz)')% 
else
    ylabel('Normalized activity')
end

% ylim([-0.06 0.06])
% title(['All Block'])
set(gca,'fontsize',20);
%%