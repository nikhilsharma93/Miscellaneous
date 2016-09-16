clc
clear all

field1='word';
field2='meaning';
%field3='part_of_speech';

value1={'engage engaged engaging';'type typed typing';'buffet buffeted';'right';'qualify';
    'absolute';    'acceptable';    'add';   
    'answer answered'  ;  'bore bear'  ;   'care' ;   'chair'  ;  'characteristic characteristics'  ; 
     'computer'  ;  'couple';     'dish dishes'  ;     'enjoy enjoyed'  ;  'enthusiasm'   ;   'i';
      'involve'  ;  'lavish'   ; 'live'  ;  'local'   ; 'man men'  ;  'married marry'   ; 'mentality' ;   'music'  ;  'offer offered'   ; 'people';
      'piano'   ; 'repeat repeated' ;   'resident residents';    'resist';    'ring' ;   'serve served'   ; 'side' ;   'strike strikes'  ;  
      'twirl twirling' ;     'village' ;     'young'};

      

value2={{'occupy or attract the attention of someone or involve someone in a conversation';'formally agree or accept to marry';'The agreement between two people who shall get married'};
    {'a category of people or things having common characteristics, or a person of specified character or nature';'write on a computer or typewriter by pressing the keys'};
    {'a meal consisting of several dishes from which guests serve themselves; a collection of many food items';'strike in a repeated manner and violently, or knock someone away, or hit someone again and again'};
    {'morally good justified or acceptable or true or correct as a fact or best or appropriate for a particular situation';'on towards or relating to the side of a human body or of a thing which is to the east when the person or thing is facing north or the right hand direction'};
    {'be entitled  or eligible to a particular benefit or privilege by fulfilling a necessary condition';'make a statement or assertion less absolute add reservations to; or make something less severe or extreme'}
    {'not qualified or diminished in any way or total or complete';'used for emphasis when expressing an opinion';'not subject to any limitation or unconditional'};
    {'able to be agreed on or suitable or moderately good or satisfactory or allowed'};
    {'join something to something else so as to increase the size number or amount increase in amount number or degree'};
    {'a thing that is said or written or done as a reaction to a question or statement or situation'; 'a solution to a problem or dilemma'};
    {'make a hole in something with a tool or by digging';'a person whose talk or behaviour is dull and uninteresting';'of a person to carry or transport or convey or shift'};
    {'the provision of what is necessary for the health or welfare or maintenance or and protection of someone or something';'feel concern or interest or attach importance to something'};
    {'a separate seat for one person typically with a back and four legs'};
    {'typical of a particular person or place or thing';'a feature or quality belonging typically to a person or place or thing and serving to identify them'};
    {'an electronic device which is capable of receiving information data in a particular form and of performing a sequence of operations in accordance with a predetermined but variable set of procedural instructions program to produce a result in the form of information or signals'};
    {'two people or things of the same sort considered together';'two people who are married or otherwise closely associated romantically';'a pair of equal and parallel forces acting in opposite directions and tending to cause rotation about an axis perpendicular to the plane containing them'};
    {'The food contained or served in a dish'};
    {'Take delight or pleasure in (an activity or occasion) or Have a pleasant time'};
    {'Intense and eager enjoyment, interest, or approval:'};
    {'The imaginary quantity equal to the square root of minus one';'The ninth letter of the alphabet.';'Used by a speaker to refer to himself or herself:'};
    {'Have or include (something) as a necessary or integral part or result: or Cause to participate in an activity or situation:'};
    {'Sumptuously rich, elaborate, or luxurious: or grand or expensive'};
    {'Remain alive: or Be alive at a specified time: or exist or Spend  life in a particular way or under particular circumstances: or Have an exciting or fulfilling life:';'Not dead or inanimate; living: or breathing'};
    {'Relating or restricted to a particular area or neighbourhood: or relating to residents of a particular region';'a local bus or train service'};
    {'An adult human male: or A male person associated with a particular place, activity, or occupation: or the male one in a couple'};
    {'Join in marriage:'};
    {'The characteristic way of thinking of a person or people'};
    {'Vocal or instrumental sounds (or both) combined in such a way as to produce beauty of form, harmony, and expression of emotion:'};
    {'Present or proffer (something) for (someone) to accept or reject as desired:';'An amount of money that someone is willing to pay for something:'};
    {'Human beings in general or considered collectively: or The members of a society without special rank or position: or persons'};
    {'A large keyboard musical instrument with a wooden case enclosing a soundboard and metal strings, which are struck by hammers when the keys are depressed. The strings vibration is stopped by dampers when the keys are released and can be regulated for length and volume by two or three pedals.'};
    {'Say again something one has already said: or  Do (something) again or more than once or in a periodic manner'};
    {'A person or people who live or lives somewhere permanently or on a long-term basis: or inhabitant or local'};
    {'Withstand the action or effect of:'};
    {'A small circular band, typically of precious metal and often set with one or more gemstones, worn on a finger as an ornament or a token of marriage or given while marrying or engaging';'A ring-shaped or circular object:'};
    {'perform duties or services for (another person or an organization): or Present (food or drink) to someone:'};
    {'A position to the left or right of an object, place, or central point:'};
    {'Hit forcibly and deliberately with one’s hand or a weapon or other implement or knock somenone ';'Cause (someone) to have a particular impression:'};
    {'Spin quickly and lightly round, especially repeatedly:'};
    {'A group of houses and associated buildings, larger than a hamlet and smaller than a town, situated in a rural area: a place where a set of people live'};
    {'Relating to or consisting of young people: young man or young woman'}};
    
    
%value3={'fgad'};

dict=struct(field1,value1,field2,value2);

stopwords_cellstring={'a', 'about', 'above', 'above', 'across', 'after', ...
    'afterwards', 'again', 'against', 'all', 'almost', 'alone', 'along', ...
    'already', 'also','although','always','am','among', 'amongst', 'amoungst', ...
    'amount',  'an', 'and', 'another', 'any','anyhow','anyone','anything','anyway', ...
    'anywhere', 'are', 'around', 'as',  'at', 'back','be','became', 'because','become',...
    'becomes', 'becoming', 'been', 'before', 'beforehand', 'behind', 'being', 'below',...
    'beside', 'besides', 'between', 'beyond', 'bill', 'both', 'bottom','but', 'by',...
    'call', 'can', 'cannot', 'cant', 'co', 'con', 'could', 'couldnt', 'cry', 'de',...
    'describe', 'detail', 'do', 'done', 'down', 'due', 'during', 'each', 'eg', 'eight',...
    'either', 'eleven','else', 'elsewhere', 'empty', 'enough', 'etc', 'even', 'ever', ...
    'every', 'everyone', 'everything', 'everywhere', 'except', 'few', 'fifteen', 'fify',...
    'fill', 'find', 'fire', 'first', 'five', 'for', 'former', 'formerly', 'forty', 'found',...
    'four', 'from', 'front', 'full', 'further', 'get', 'give', 'go', 'had', 'has', 'hasnt',...
    'have', 'he', 'hence', 'her', 'here', 'hereafter', 'hereby', 'herein', 'hereupon', ...
    'hers', 'herself', 'him', 'himself', 'his', 'how', 'however', 'hundred', 'ie', 'if',...
    'in', 'inc', 'indeed', 'interest', 'into', 'is', 'it', 'its', 'itself', 'keep', 'last',...
    'latter', 'latterly', 'least', 'less', 'ltd', 'made', 'many', 'may', 'me', 'meanwhile',...
    'might', 'mill', 'mine', 'more', 'moreover', 'most', 'mostly', 'move', 'much', 'must',...
    'my', 'myself', 'name', 'namely', 'neither', 'never', 'nevertheless', 'next', 'nine',...
    'no', 'nobody', 'none', 'noone', 'nor', 'not', 'nothing', 'now', 'nowhere', 'of', 'off',...
    'often', 'on', 'once', 'one', 'only', 'onto', 'or', 'other', 'others', 'otherwise',...
    'our', 'ours', 'ourselves', 'out', 'over', 'own','part', 'per', 'perhaps', 'please',...
    'put', 'rather', 're', 'same', 'see', 'seem', 'seemed', 'seeming', 'seems', 'serious',...
    'several', 'she', 'should', 'show', 'side', 'since', 'sincere', 'six', 'sixty', 'so',...
    'some', 'somehow', 'someone', 'something', 'sometime', 'sometimes', 'somewhere', ...
    'still', 'such', 'system', 'take', 'ten', 'than', 'that', 'the', 'their', 'them',...
    'themselves', 'then', 'thence', 'there', 'thereafter', 'thereby', 'therefore', ...
    'therein', 'thereupon', 'these', 'they', 'thick', 'thin', 'third', 'this', 'those',...
    'though', 'three', 'through', 'throughout', 'thru', 'thus', 'to', 'together', 'too',...
    'top', 'toward', 'towards', 'twelve', 'twenty', 'two', 'un', 'under', 'until', 'up',...
    'upon', 'us', 'very', 'via', 'was', 'we', 'well', 'were', 'what', 'whatever', 'when',...
    'whence', 'whenever', 'where', 'whereafter', 'whereas', 'whereby', 'wherein',...
    'whereupon', 'wherever', 'whether', 'which', 'while', 'whither', 'who', 'whoever',...
    'whole', 'whom', 'whose', 'why', 'will', 'with', 'within', 'without', 'would', 'yet',...
    'you', 'your', 'yours', 'yourself', 'yourselves', 'the','did','things','i'};

line=regexprep(lower(input('Enter the line \n','s')),'[^a-zA-z\s]','');
word=lower(input('\nEnter the word whose meaning is required \n','s'));

s1=strfind(line,word);
s2=s1+length(word);
str_bef=line(1:s1-2);
str_aft=line(s2:length(line));
str_wo_word=strcat(str_bef,str_aft);
str_wo_word_spt=setdiff(strsplit(str_wo_word),stopwords_cellstring);
neighbor='';

for i=1:length(str_wo_word_spt)
    temp_loc=find(~cellfun('isempty',regexp(value1,str_wo_word_spt(i))));
    [temp_nom,useless1]=size((dict(temp_loc).meaning));
    for j=1:temp_nom
        neighbor=horzcat(neighbor,regexprep(lower(dict(temp_loc).meaning(j)),'[^a-zA-z\s]',''));
    end
     neighbor=horzcat(neighbor,regexprep(lower(str_wo_word_spt(i)),'[^a-zA-z\s]',''));
end
neighbor=strjoin(neighbor);

location=find(~cellfun('isempty',regexp(value1,word)));
[nom,useless2]=size((dict(location).meaning));
if nom==1
    disp('The meaning of the word is:');
    str=sprintf('\n');
    disp(str);
    disp(dict(location).meaning);
else
    max_count=0;
    context_loc=0;
    for i=1:nom
        match_count=word_match(char(dict(location).meaning(i)),neighbor,stopwords_cellstring);
        if match_count>max_count
            max_count=match_count;
            context_loc=i;
        end
    end
end

if context_loc==0
    str=sprintf('\n The meaning of the word could not be determined \n');
    disp(str)
else
    str=sprintf('\n');
    disp(str);
    str1=sprintf('The number of intersects is %d \n',max_count);
    disp(str1)
    disp('The meaning of the word in the given context is:');
    disp(str);    
    disp(regexprep(lower(dict(location).meaning(context_loc)),'[^a-zA-z\s,]',''));
end
