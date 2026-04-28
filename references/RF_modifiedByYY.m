close all;
clear; clc;
% Root= 'F:\Yami\240625';% 'F:\170614';
folderlist={


'F:\COCO\231022';
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
% 'F:\COCO\231215';
% 'F:\COCO\231217';
% 'F:\COCO\231218';
% 'F:\COCO\231219';
% 'F:\COCO\231220';

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
% 'F:\COCO\231227';
% 'F:\COCO\231228';
% 'F:\COCO\231229';
% 'F:\COCO\231231';
% % % % % % % % % % % % % % % 
% % 
% % % % % % % % % % % % % % % %%135deg puff
% % % % % % % 'F:\COCO\240111';
% 'F:\COCO\240112';
% 'F:\COCO\240114';
% 'F:\COCO\240115';
% 'F:\COCO\240116';
% 'F:\COCO\240117';
% 'F:\COCO\240118';

% 'F:\COCO\240124';
% 'F:\COCO\240125';

%%45puff yami
% 'F:\Yami\240625';
% 'F:\Yami\240618';
% 'F:\Yami\240620';
% 'F:\Yami\240621';
% 'F:\Yami\240623';
% 
% % % % 
'F:\Yami\240627';
% 'F:\Yami\240628';  %
% 'F:\Yami\240630';  
% 'F:\Yami\240701';
% 'F:\Yami\240702';
% % % 
% % % %%135puff yami  all good
% 'F:\Yami\240704';  %
% 'F:\Yami\240705';  %
% 'F:\Yami\240706';  %
% 'F:\Yami\240708';
% 'F:\Yami\240709';

%%%9bar puff
% 'F:\Yami\240810';
% 'F:\Yami\240812';
% 'F:\Yami\240813';
% 'F:\Yami\240814';
% 'F:\Yami\240816';
% 'F:\Yami\240819';
% 'F:\Yami\240821';
% 'F:\Yami\240822';
% 
% 
% %%%1bar puff
% 
% 'F:\Yami\240828';
% 'F:\Yami\240829';
% 'F:\Yami\240902';
% 'F:\Yami\240903';
% 'F:\Yami\240906';
% 'F:\Yami\240907';
% 'F:\Yami\240911';
% 'F:\Yami\240912';
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

% 
% 'F:\COCO\231022';
% 'F:\COCO\231023';
% 'F:\COCO\231024';
% 'F:\COCO\231026';
% 'F:\COCO\231027';
% 'F:\COCO\231030';
% 
% 
% 
% %%%9bar puff
% 
% %%9bar puff
% 'F:\COCO\231127';
% 'F:\COCO\231129';
% 'F:\COCO\231130';
% 'F:\COCO\231201';
% 'F:\COCO\231203';
% 'F:\COCO\231206';


    };
for iday=1:numel(folderlist)
    iday
    Root=[];
    strRFPath={};
Root= folderlist{iday};% 'F:\170614
OriTunStep=0;   % 0: 22.5deg Orituning  1: 15deg Orituning
%% Parameters and paths
strCmpPath ='E:\file\240524 Yami array\SN 4566-004425.cmp';
% strCmpPath = 'F:\COCO\SN 4566-0905.cmp';%
% strCmpPath ='E:\file\LIZhhmatlab\emotion monkey matlab\SN 4566-001632.cmp';%SN 4566-001630 %'E:\file\LIZhhmatlab\emotion monkey matlab\SN 4566-001303+Probe MK2.cmp';
strRFPath.Xp = {
     [Root '\Xtuning000']
% Add more file here
};
strRFPath.Yp = {
     [Root '\Ytuning001']  
% Add more file here
};
strRFPath.Ori = {    
   [Root '\ORItuning002']                                                                                                                                                                                                                                                                                                                                                                                                                                                           
% Add more file here
};
% 
%% Load array map   
% cmpinfo = LoadCmp(strCmpPath,2,0); % There are 2 sub arrays in MG
% elec{1,1} = [cmpinfo{1,1}.RealElec;cmpinfo{2,1}.RealElec];
% elec{1,1} =elec{1,1}';
%elec{1,1} =elec{1,1}(1:49);        %mild PFC channel i ndex



% cmppath =  'E:\file\LIZhhmatlab\emotion monkey matlab\SN 4566-001303+Probe MK2.cmp';%%%180725
% cmppath = 'E:\data\SN 4566-001303+Probe MK2.cmp';
% cmppath='F:\SN 4566-001303+Probe MK2.cmp';
cmpinfo = LoadCmp(strCmpPath,1,0);
% elec{1,1} = [cmpinfo{1,1}.RealElec];
% elec{1,1} =cmpinfo{1,1}.RealElec([1:6 10:15],:);
%%yami
elecV4{1,1}=cmpinfo{1,1}.RealElec(1:8,:);
elecV1{1,1}=cmpinfo{1,1}.RealElec(11:18,:);
%%coco
% elecV4{1,1}=cmpinfo{1,1}.RealElec(:,1:5);
% elecV1{1,1}=cmpinfo{1,1}.RealElec(:,6:10);
unitV1{1,1} = lower( char(zeros(size(elecV1{1,1},1),size(elecV1{1,1},2))+84) );  %'t'
unitV4{1,1} = lower( char(zeros(size(elecV4{1,1},1),size(elecV4{1,1},2))+84) );  %'t'

% AlexV4Arraymap = load('Y:\ANALYSIS\GPPL_Post\AlexV4Arraymap.mat');
% AlexV4Arraymap = AlexV4Arraymap.ans;
% elec{1,1} =AlexV4Arraymap;     %mild V4 channel index
% 
% unit{1,1} = lower( char(zeros(1,64)+84) );  %'t'  +84   ¡®A¡¯ +65 'U' +85

% XP
for iDay = 1:max(size(strRFPath.Xp))
    % Get stimulus settings from log file
    LogPath = strcat(strRFPath.Xp{iDay},'.log');
    RFLog = LoadLog(LogPath);
    assert(RFLog.Var.TestID(1)==1||RFLog.Var.TestID(1)==31||RFLog.Var.TestID(1)==51) % Make sure the file is a Xp scanning
    StimOnTime = RFLog.Timing.PreFrame/100;
    StimOffTime = (RFLog.Timing.PreFrame+RFLog.Timing.OnFrame)/100;
    StartValue = RFLog.Var.StartValue(1);
    EndValue = RFLog.Var.EndValue(1);
    NumberofPoints = RFLog.Var.NumberofPoints(1);
    CenterValue = RFLog.RF.Xp-RFLog.RF.FpXp;
    win = [StimOnTime StimOffTime];
    stim = linspace(StartValue,EndValue,NumberofPoints)+CenterValue;
    
    % Load nev
    NevPath = strcat(strRFPath.Xp{iDay},'.nev');
    %LoadSpike(NevPath,1:96,0);
    
    % Fit curves
    xparamV1{iDay} = GetPref(NevPath,stim,elecV1,unitV1,win,0);
    xparamV4{iDay} = GetPref(NevPath,stim,elecV4,unitV4,win,0);
end
%% YP
for iDay = 1:max(size(strRFPath.Yp))
    % Get stimulus settings from log file
    LogPath = strcat(strRFPath.Yp{iDay},'.log');
    RFLog = LoadLog(LogPath);
    assert(RFLog.Var.TestID(1)==2||RFLog.Var.TestID(1)==32||RFLog.Var.TestID(1)==52) % Make sure the file is a Yp scanning
    StimOnTime = RFLog.Timing.PreFrame/100;
    StimOffTime = (RFLog.Timing.PreFrame+RFLog.Timing.OnFrame)/100;
    StartValue = RFLog.Var.StartValue(1);
    EndValue = RFLog.Var.EndValue(1);
    NumberofPoints = RFLog.Var.NumberofPoints(1);
    CenterValue = RFLog.RF.Yp-RFLog.RF.FpYp;
    win = [StimOnTime StimOffTime];  
    stim = linspace(StartValue,EndValue,NumberofPoints)+CenterValue;
    
    NevPath = strcat(strRFPath.Yp{iDay},'.nev');
    %LoadSpike(NevPath,1:96,0);
    
  yparamV1{iDay} = GetPref(NevPath,stim,elecV1,unitV1,win,0);
  yparamV4{iDay} = GetPref(NevPath,stim,elecV4,unitV4,win,0);
end
%% ORI
for iDay = 1:max(size(strRFPath.Ori))
    LogPath = strcat(strRFPath.Ori{iDay},'.log');
    RFLog = LoadLog(LogPath);
    assert(RFLog.Var.TestID(1)==0) % Make sure the file is a Ori scanning
    StimOnTime = RFLog.Timing.PreFrame/100;
    StimOffTime = (RFLog.Timing.PreFrame+RFLog.Timing.OnFrame)/100;
    StartValue = RFLog.Var.StartValue(1);
    EndValue = RFLog.Var.EndValue(1);
    NumberofPoints = RFLog.Var.NumberofPoints(1);
    CenterValue = RFLog.RF.Ori;
    win = [StimOnTime StimOffTime];
    stim = linspace(StartValue,EndValue,NumberofPoints);% Must be -180~180, otherwise the file will not be recognized as Ori
    
    NevPath = strcat(strRFPath.Ori{iDay},'.nev');
    %LoadSpike(NevPath,1:96,0);
    win=[0.2 1.0];
    
    
    oparamV1{iDay} = GetPref(NevPath,stim,elecV1,unitV1,win,0);
    oparamV1{iDay}{4} = oparamV1{iDay}{4}; %+CenterValue; %%question
    
    oparamV4{iDay} = GetPref(NevPath,stim,elecV4,unitV4,win,0);
    oparamV4{iDay}{4} = oparamV4{iDay}{4}; %+CenterValue; %%question
    %%
%     kaa=cell2mat(elecV4);
%     kaaidx=kaa~=0;
%     kaa=kaa(kaaidx);
%     for k=1:numel(kaa)
%         spikeinfo=BinSpike(NevPath,kaa(k),'t',win,0.01);
%         splitspk=SplitInfo(spikeinfo,[1 0 1 0]);
%         mori=[];
%          for m = 1:17
%                 
%                     mori=[mori; splitspk{1,m}{1,1}.Train];
%                     
%          end
%             mmori(:,k)=mean(mori)';
%     end
%     figure
%     for k=1:numel(kaa)
%    subplot(6,8,k);
%     
% 
% plot(mmori(:,k),'r')
%     end
    
    
end
%% Save RFs in mat
% save('xparam','xparam');
% save('yparam','yparam');
% save('oparam','oparam');

%% DrawRFs

iDay = 1;
% load xparam;
% load yparam;
% load oparam;

threshold = 0.7;
% thresholdV4 = 0.6;
V1XYvalid = xparamV1{iDay}{7}>threshold & yparamV1{iDay}{7}>threshold ;%& oparamV1{iDay}{7}>threshold; % Find out which channels have a good fitting
V4XYvalid = xparamV4{iDay}{7}>threshold & yparamV4{iDay}{7}>threshold ;%& oparamV4{iDay}{7}>threshold;

V1XOYvalid = xparamV1{iDay}{7}>threshold | yparamV1{iDay}{7}>threshold ;%& oparamV1{iDay}{7}>threshold; % Find out which channels have a good fitting
V4XOYvalid = xparamV4{iDay}{7}>threshold | yparamV4{iDay}{7}>threshold ;%& oparamV4{iDay}{7}>threshold;

V4Yvalid = yparamV4{iDay}{7}>threshold ;%& oparamV4{iDay}{7}>threshold;
V4Xvalid = xparamV4{iDay}{7}>threshold ;%& oparamV4{iDay}{7}>threshold;
V1Yvalid = yparamV1{iDay}{7}>threshold ;%& oparamV4{iDay}{7}>threshold;
V1Xvalid = xparamV1{iDay}{7}>threshold ;%& oparamV4{iDay}{7}>threshold;
numV4Xvalid=sum(sum(V4Xvalid));
numV1Xvalid=sum(sum(V1Xvalid));
numV4Yvalid=sum(sum(V4Yvalid));
numV1Yvalid=sum(sum(V1Yvalid));
V1valid=xparamV1{iDay}{7}>threshold & yparamV1{iDay}{7}>threshold&oparamV1{iDay}{7}>threshold;
V4valid=xparamV4{iDay}{7}>threshold & yparamV4{iDay}{7}>threshold&oparamV4{iDay}{7}>threshold; 
V1orivalid=oparamV1{iDay}{7}>threshold;
V4orivalid=oparamV4{iDay}{7}>threshold; 
numV1XYvalid=sum(sum(V1XYvalid));
numV4XYvalid=sum(sum(V4XYvalid));
numV1valid=sum(sum(V1valid));
numV4valid=sum(sum(V4valid));
numV1ORIvalid=sum(sum(V1orivalid));
numV4ORIvalid=sum(sum(V4orivalid));
% validElecIDs = xparam{iDay}{7}>threshold & yparam{iDay}{7}>threshold & oparam{iDay}{7}>threshold; % Find out which channels have a good fitting
% % validElecIDs = (~isoutlier(yparam{iDay}{4}(validElecIDs))) & validElecIDs;
figure;
barLen = 0.3;
for iElec = 1:48  %yami 64  coco48
    if V1XYvalid(iElec) %validV1ElecIDs(iElec) 
        x = xparamV1{iDay}{4}(iElec);
        y = yparamV1{iDay}{4}(iElec);  
%         o = oparam{iDay}{4}(iElec)/180*pi;
%         line([x-barLen*cos(o) x+barLen*cos(o)],[y-barLen*sin(o) y+barLen*sin(o)],'LineWidth',2)
        axis equal;
%         xRadii = 2*1.96*xparamV1{1, 1}{1, 5}(iElec);
%         yRadii = 2*1.96*yparamV1{1, 1}{1, 5}(iElec); 
        
        xRadii = 1.96*xparamV1{1, 1}{1, 5}(iElec);
        yRadii = 1.96*yparamV1{1, 1}{1, 5}(iElec); 
        rectangle('Position',[x-0.5*xRadii y-0.5*yRadii xRadii yRadii],'Curvature',0.2,'EdgeColor','g')
        text(double(x),double(y),num2str(elecV1{1,1}(iElec)))
        hold on;
    end
end

for iElec = 1:48  %yami 64  coco48
    if V4Yvalid(iElec)%validV4ElecIDs(iElec) 
        x = xparamV4{iDay}{4}(iElec);
        y = yparamV4{iDay}{4}(iElec);  
%         o = oparam{iDay}{4}(iElec)/180*pi; 
%         line([x-barLen*cos(o) x+barLen*cos(o)],[y-barLen*sin(o) y+barLen*sin(o)],'LineWidth',2)
        axis equal;
        xRadii = 2*1.96*xparamV4{1, 1}{1, 5}(iElec);
        yRadii = 2*1.96*yparamV4{1, 1}{1, 5}(iElec); 
        
%         xRadii = 1.96*xparamV4{1, 1}{1, 5}(iElec);
%         yRadii = 1.96*yparamV4{1, 1}{1, 5}(iElec); 
        rectangle('Position',[x-0.5*xRadii y-0.5*yRadii xRadii yRadii],'Curvature',0.2,'EdgeColor','b')
        text(double(x),double(y),num2str(elecV4{1,1}(iElec)))
        hold on;
    end
end
 %%%%%%
scatter(xparamV1{iDay}{4}(V1XYvalid),yparamV1{iDay}{4}(V1XYvalid),200,'.r')
scatter(xparamV4{iDay}{4}(V4Yvalid),yparamV4{iDay}{4}(V4Yvalid),200,'.g')
xlabel('Azimuth(deg)')  
ylabel('Elevation(deg)')
axis([-8,2,-8,2])
set(gca,'FontSize',30,'FontWeight','bold');
% axis equal;
%axis([-5.5 -3.5 -4 -2.5]);

%%save the validelec
anchor=strfind(strRFPath.Xp,'\');
path=strRFPath.Xp{1}(1:anchor{1}(end)); 
% save([path 'V1XYvalid3'],'V1XYvalid','-v7.3');
% save([path 'V4XYvalid3'],'V4XYvalid','-v7.3');
% save([path 'V1XOYvalid3'],'V1XOYvalid','-v7.3');
% save([path 'V4XOYvalid3'],'V4XOYvalid','-v7.3');
% save([path 'V1orivalid3'],'V1orivalid','-v7.3');
% save([path 'V4orivalid3'],'V4orivalid','-v7.3');
% save([path 'V1oritun3'],'oparamV1','-v7.3');
% save([path 'V4oritun3'],'oparamV4','-v7.3');
% save([path 'V1xtun3'],'xparamV1','-v7.3');
% save([path 'V4xtun3'],'xparamV4','-v7.3');
% save([path 'V1ytun3'],'yparamV1','-v7.3');
% save([path 'V4ytun3'],'yparamV4','-v7.3');
end
% save([path 'XYvalidid'],'XYvalidid','-v7.3');
% save([path 'ORIvalidid'],'ORIvalidid','-v7.3');